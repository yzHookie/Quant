import ccxt
import os
import datetime
import time
import pandas as pd
import pymongo

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


def crawl_binance_datas(symbol, start_time, end_time):
    exchange = ccxt.binance(
        {"proxies": {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}}
    )
    file_dir = os.path.join(current_dir_path, symbol.replace("/", ""))
    print(file_dir)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")
    start_time_stamp = int(time.mktime(start_time.timetuple())) * 1000
    end_time_stamp = int(time.mktime(end_time.timetuple())) * 1000

    limit_count = 100
    cnt = 10
    while cnt:
        cnt -= 1
        try:
            print(start_time_stamp)
            data = exchange.fetch_ohlcv(
                symbol, timeframe="1m", since=start_time_stamp, limit=limit_count
            )
            df = pd.DataFrame(data)
            df.rename(
                columns={
                    0: "open_time",
                    1: "open",
                    2: "high",
                    3: "low",
                    4: "close",
                    5: "volume",
                },
                inplace=True,
            )

            start_time_stamp = int(df.iloc[-1]["open_time"])
            file_name = str(start_time_stamp) + ".csv"
            save_file_path = os.path.join(file_dir, file_name)
            print(f"文件保存路径为: {save_file_path}")
            df.set_index("open_time", drop=True, inplace=True)
            df.to_csv(save_file_path)

            if start_time_stamp > end_time_stamp:
                print("完成数据请求")
                break
            time.sleep(1)
        except Exception as error:
            print(error)


def sample_datas(symbol):
    """
    :param exchange_name:
    :param symbol:
    :return:
    """
    file_dir = os.path.join(current_dir_path, symbol.replace("/", ""))
    print(file_dir)
    file_paths = []
    for root, dirs, files in os.walk(file_dir):
        if files:
            for file in files:
                if file.endswith(".csv"):
                    file_paths.append(os.path.join(file_dir, file))

    file_paths = sorted(file_paths)
    all_df = pd.DataFrame()

    for file in file_paths:
        df = pd.read_csv(file)
        all_df = pd.concat([all_df, df], ignore_index=True)

    all_df = all_df.sort_values(by="open_time", ascending=True)

    print(all_df)

    return all_df


def clear_datas(symbol):
    file_dir = os.path.join(current_dir_path, symbol.replace("/", ""))
    df = sample_datas(symbol)
    # print(df)
    # exit()
    # df['open_time'] = df['open_time'].apply(lambda x: time.mktime(x.timetuple()))
    # # 日期.timetuple() 这个用法 通过它将日期转换成时间元组
    # # print(df)
    # df['open_time'] = df['open_time'].apply(lambda x: (x // 60) * 60 * 1000)
    df["open_time"] = df["open_time"].apply(lambda x: (x // 60) * 60)  # 获取整分的数据.
    print(df)
    df["Datetime"] = pd.to_datetime(df["open_time"], unit="ms") + pd.Timedelta(
        hours=8
    )  # 把UTC时间转成北京时间.
    df["Datetime"] = df["Datetime"].apply(
        lambda x: str(x)[0:19]
    )  # 2018-11-15 00:47:0034, 通过截取字符串长度.
    df.drop_duplicates(subset=["open_time"], inplace=True)
    df.set_index("Datetime", inplace=True)
    print("*" * 20)
    print(df)
    # df.to_csv(os.path.join(file_dir, "1min_data.csv"))
    # 自定义主键
    data = df.to_dict(orient="records")
    for docment in data:
        docment["_id"] = docment["open_time"]
    db_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = db_client["quant"]
    db_collection = db["test"]
    db_collection.insert_many(data)


if __name__ == "__main__":
    # crawl_binance_datas("BTC/USDT", "2024-4-10", "2024-4-12")
    clear_datas("BTC/USDT")
