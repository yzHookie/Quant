import requests
import json
import time
import hmac
import hashlib
from enum import Enum
import pymongo


class Interval(Enum):
    MIN_1 = "1m"
    MIN_3 = "3m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_4 = "4h"
    HOUR_6 = "6h"
    HOUR_8 = "8h"
    HOUR_12 = "12h"
    DAY_1 = "1d"
    DAY_3 = "3d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    STOP_MARKET = "STOP_MARKET"


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


class PositionSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTX = "GTX"


class RequestMethod(Enum):
    GET = "get"
    POST = "post"
    DELETE = "delete"
    PUT = "put"


class BinanceFutureHttpClient:
    def __init__(
        self,
        base_url="https://fapi.binance.com",
        api_key=None,
        api_secret=None,
        timeout=5,
    ):
        self.base_url_ = base_url
        self.key_ = api_key
        self.secret_ = api_secret
        self.timeout_ = timeout

    def GetTimeStamp(self):
        return int(time.time() * 1000)

    def BuildParamsUrl(self, params: dict):
        requery = "&".join([f"{key}={params[key]}" for key in params.keys()])
        return requery

    def Request(self, method: RequestMethod, path, params=None, verify=False):
        url = self.base_url_ + path
        if params:
            url += "?" + self.BuildParamsUrl(params)

        # 需要签名的api
        if verify:
            query_str = self.BuildParamsUrl(params)
            signature = hmac.new(
                self.secret_.encode("utf-8"),
                msg=query_str.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).hexdigest()
            url += "&signature=" + signature
        print(url)
        headers = {"X-MBX-APIKEY": self.key_}
        return requests.request(
            method.value, url, headers=headers, timeout=self.timeout_
        ).json()

    def GetServerStatus(self):
        path = "/fapi/v1/ping"
        return self.Request(RequestMethod.GET, path)

    def GetServerTime(self):
        path = "/fapi/v1/time"
        return self.Request(RequestMethod.GET, path)

    def GetExchangeInfo(self):
        path = "/fapi/v1/exchangeInfo"
        return self.Request(RequestMethod.GET, path)

    def GetMarketDepth(self, symbol, limit=5):
        limits = [5, 10, 20, 50, 100, 500, 1000]
        if limit not in limits:
            limit = 5
        path = "/fapi/v1/depth"
        params = {"symbol": symbol, "limit": limit}
        return self.Request(RequestMethod.GET, path, params)

    def GetKlines(
        self, symbol, interval: Interval, start_time=None, end_time=None, limit=500
    ):
        path = "/fapi/v1/klines"
        params = {"symbol": symbol, "interval": interval.value, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return self.Request(RequestMethod.GET, path, params)

    def GetTickerPrice(self, symbol=None):
        path = "/fapi/v1/ticker/price"
        params = None
        if symbol:
            params = {"symbol": symbol}
        return self.Request(RequestMethod.GET, path, params)

    def GetBookTicker(self, symbol=None):
        path = "/fapi/v1/ticker/bookTicker"
        params = None
        if symbol:
            params = {"symbol": symbol}
        return self.Request(RequestMethod.GET, path, params)

    def PostPlaceOrder(
        self,
        symbol,
        side: Side,
        position_side: PositionSide,
        order_type: OrderType,
        quantity,
        price=None,
        stop_price=None,
        time_inforce=TimeInForce.GTC,
        recv_window=5000,
    ):
        path = "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "side": side.value,
            "positionSide": position_side.value,
            "type": order_type.value,
            "quantity": quantity,
            "recvWindow": recv_window,
            "timestamp": self.GetTimeStamp(),
        }
        # 限价订单
        if order_type == OrderType.LIMIT:
            params["timeInForce"] = time_inforce.value
            if price > 0:
                params["price"] = price
            else:
                raise ValueError("price is empty")

        # 市价订单
        if order_type == OrderType.MARKET:
            pass

        # 止损市订单
        if order_type == OrderType.STOP_MARKET:
            if stop_price > 0:
                params["stopPrice"] = stop_price
            else:
                raise ValueError("stop price is empty")

        # 止损现价单
        if order_type == OrderType.STOP:
            if price > 0:
                params["price"] = price
            else:
                raise ValueError("price is empty")

            if stop_price > 0:
                params["stopPrice"] = stop_price
            else:
                raise ValueError("stop price is empty")

        return self.Request(RequestMethod.POST, path, params, verify=True)

    def GetOrder(self, symbol, order_id, recv_window=5000):
        path = "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "recvWindow": recv_window,
            "timestamp": self.GetTimeStamp(),
            "orderId": order_id,
        }
        return self.Request(RequestMethod.GET, path, params, verify=True)

    def DeleteOrder(self, symbol, order_id, recv_window=5000):
        path = "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "recvWindow": recv_window,
            "timestamp": self.GetTimeStamp(),
            "orderId": order_id,
        }
        return self.Request(RequestMethod.DELETE, path, params, verify=True)

    def GetOpenOrder(self, symbol, order_id, recv_window=5000):
        path = "/fapi/v1/openOrder"
        params = {
            "symbol": symbol,
            "recvWindow": recv_window,
            "timestamp": self.GetTimeStamp(),
            "orderId": order_id,
        }
        return self.Request(RequestMethod.GET, path, params, verify=True)

    def GetOpenOrders(self, symbol=None, recv_window=5000):
        path = "/fapi/v1/openOrders"
        params = {
            "recvWindow": recv_window,
            "timestamp": self.GetTimeStamp(),
        }
        if symbol:
            params["symbol"] = symbol
        return self.Request(RequestMethod.GET, path, params, verify=True)


if __name__ == "__main__":
    key = "OGx3Q7YnvI6GZyGA8I9FS4MYspYep00g72yjvqyg6Ze6YtyL2rmU8GV6ke2YeK95"
    secret = "hy1eqcfiECpyDCbuNN5HZLkOnzE2ljnyK1SOedB8256F7M5hB7GHTdUotY7XnScN"
    bf = BinanceFutureHttpClient(api_key=key, api_secret=secret)
    db_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = db_client["quant"]
    db_collection = db["test"]
    # server_status = bf.GetServerStatus()
    # print(server_status)
    # server_time = bf.GetServerTime()
    # print(server_time)
    # exchange_info = bf.GetExchangeInfo()
    # print(exchange_info)
    market_depth = bf.GetMarketDepth("BTCUSDT", 10)
    print(market_depth)
    db_collection.insert_one(market_depth)
    # klines = bf.GetKlines("BTCUSDT", Interval.MIN_1)
    # print(klines)
    # ticker_price = bf.GetTickerPrice("BTCUSDT")
    # print(ticker_price)
    # book_ticker = bf.GetBookTicker("BTCUSDT")
    # print(book_ticker)
    # post_order_info = bf.PostPlaceOrder("BTCUSDT", Side.BUY, OrderType.LIMIT, 1, 10000)
    # print(post_order_info)
