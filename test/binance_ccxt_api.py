import ccxt

exchange = ccxt.binance(
    {
        "proxies": {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        },
    }
)
# 尝试获取账户信息来测试连接
balance = exchange.fetch_balance(params={"configType": "futures"})
print(balance["USDT"])
