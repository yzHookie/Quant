import requests
import time
import pandas as pd

pd.set_option("expand_frame_repr", False)

BASE_URL = "https://fapi.binance.com"
kline = "/fapi/v1/klines"


def func1():
    kline_url = BASE_URL + kline + "?" + "symbol=BTCUSDT&interval=1h&limit=5"
    print(kline_url)

    resp = requests.get(kline_url)
    print(resp.json())
    df = pd.DataFrame(resp.json())
    print(df)


def func2():
    limit = 10
    end_time = int(time.time() // 60 * 60 * 1000)
    start_time = end_time - limit * 60 * 1000
    url = (
        BASE_URL
        + kline
        + "?symbol=BTCUSDT&interval=1m&limit="
        + str(limit)
        + "&startTime="
        + str(start_time)
        + "&endTime="
        + str(end_time)
    )
    print(url)
    resp = requests.get(url)
    df = pd.DataFrame(resp.json())
    print(df)
    df.to_csv(str(end_time) + ".csv")


func2()
