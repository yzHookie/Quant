import ccxt

exchange = ccxt.binance(
    {
        "apiKey": "OGx3Q7YnvI6GZyGA8I9FS4MYspYep00g72yjvqyg6Ze6YtyL2rmU8GV6ke2YeK95",
        "secret": "hy1eqcfiECpyDCbuNN5HZLkOnzE2ljnyK1SOedB8256F7M5hB7GHTdUotY7XnScN",
        "proxies": {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        },
    }
)
# 尝试获取账户信息来测试连接
balance = exchange.fetch_balance(params={"configType": "futures"})
print(balance["USDT"])
