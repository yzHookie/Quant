import requests
import json
import time
import hmac
import hashlib
from enum import Enum


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


class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTX = "GTX"


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

    def GetServerStatus(self):
        path = "/fapi/v1/ping"
        url = self.base_url_ + path
        response_data = requests.get(url, timeout=self.timeout_).json()
        return response_data

    def GetServerTime(self):
        path = "/fapi/v1/time"
        url = self.base_url_ + path
        response_data = requests.get(url, timeout=self.timeout_).json()
        return response_data

    def GetExchangeInfo(self):
        path = "/fapi/v1/exchangeInfo"
        url = self.base_url_ + path
        response_data = requests.get(url, timeout=self.timeout_).json()
        return response_data

    def GetMarketDepth(self, symbol, limit=5):
        limits = [5, 10, 20, 50, 100, 500, 1000]
        if limit not in limits:
            limit = 5
        path = "/fapi/v1/depth"
        url = self.base_url_ + path
        params = {"symbol": symbol, "limit": limit}
        response_data = requests.get(url, params=params, timeout=self.timeout_).json()
        return response_data

    def GetKlines(
        self, symbol, interval: Interval, start_time=None, end_time=None, limit=500
    ):
        path = "/fapi/v1/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        url = self.base_url_ + path
        response_data = requests.get(url, params=params, timeout=self.timeout_).json()
        return response_data

    def GetTickerPrice(self, symbol=None):
        path = "/fapi/v1/ticker/price"
        url = self.base_url_ + path
        if symbol:
            url += "?symbol=" + symbol
        response_data = requests.get(url, timeout=self.timeout_).json()
        return response_data

    def GetBookTicker(self, symbol=None):
        path = "/fapi/v1/ticker/bookTicker"
        url = self.base_url_ + path
        if symbol:
            url += "?symbol=" + symbol
        response_data = requests.get(url, timeout=self.timeout_).json()
        return response_data

    def PlaceOrder(
        self,
        symbol,
        side: Side,
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

        query_str = ""
        for key in params.keys():
            query_str += f"{key}={params[key]}&"
        query_str = query_str[0:-1]
        signature = hmac.new(
            self.secret_.encode("utf-8"),
            msg=query_str.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        query_str += "&signature=" + signature
        url = self.base_url_ + path + "?" + query_str
        print(url)
        headers = {"X-MBX-APIKEY": self.key_}
        response_data = requests.post(
            url, headers=headers, timeout=self.timeout_
        ).json()
        print(response_data)
        return response_data


if __name__ == "__main__":
    key = "OGx3Q7YnvI6GZyGA8I9FS4MYspYep00g72yjvqyg6Ze6YtyL2rmU8GV6ke2YeK95"
    secret = "hy1eqcfiECpyDCbuNN5HZLkOnzE2ljnyK1SOedB8256F7M5hB7GHTdUotY7XnScN"
    bf = BinanceFutureHttpClient(api_key=key, api_secret=secret)
    # server_status = bf.GetServerStatus()
    # print(server_status)
    # server_time = bf.GetServerTime()
    # print(server_time)
    # exchange_info = bf.GetExchangeInfo()
    # print(exchange_info)
    # market_depth = bf.GetMarketDepth("BTCUSDT", 10)
    # print(market_depth)
    # klines = bf.GetKlines("BTCUSDT", Interval.MIN_1)
    # print(klines)
    # ticker_price = bf.GetTickerPrice("BTCUSDT")
    # print(ticker_price)
    # book_ticker = bf.GetBookTicker("BTCUSDT")
    # print(book_ticker)
    bf.PlaceOrder("BTCUSDT", Side.BUY, OrderType.LIMIT, 1, 10000)
