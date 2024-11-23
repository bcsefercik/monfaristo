import requests

API_URL = "http://127.0.0.1:8000/"

# create user
EMAIL = "try@try.com"
PASSWORD = "trytry123"

# create user
response = requests.post(
    API_URL + "user/create",
    json={
        "email": EMAIL,
        "first_name": "try",
        "last_name": "123",
        "password": PASSWORD,
    },
)

USER_ID = None

if response.ok:
    USER_ID = response.json()["id"]
    print(f"{response.status_code}: User (ID: {USER_ID}) created successfully")

# get token
response = requests.post(
    API_URL + "user/token",
    data={"username": EMAIL, "password": PASSWORD},
)

ACCESS_TOKEN = response.json().get("access_token")

print(f"{response.status_code}: ACCESS_TOKEN: {ACCESS_TOKEN}")

# create currencies
CURRENCIES = [
    {"title": "Turtkish Lira", "code": "TRY", "symbol": "₺"},
    {"title": "United States Dollar", "code": "USD", "symbol": "$"},
    {"title": "Euro", "code": "EUR", "symbol": "€"},
    {"title": "Tether", "code": "USDT", "symbol": "₮"},
    {"title": "Gold", "code": "XAU", "symbol": "XAU"},
    {"title": "Bitcoin", "code": "BTC", "symbol": "₿"},
]
for currency in CURRENCIES:
    response = requests.post(
        API_URL + "currency",
        json=currency,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    if response.ok:
        print(f"{response.status_code}: {currency['code']} created successfully")


# create platforms
PLATFORMS = [
    {
        "title": "Türkiye İş Bankası",
        "description": "Türkiye İş Bankası or simply İşbank is Turkey's largest bank.",
        "url": "https://www.isbank.com.tr/",
    },
    {
        "title": "Garanti BBVA",
        "description": "Garanti BBVA or simply Garanti is Turkey's second largest private bank.",
        "url": "https://www.garantibbva.com.tr/",
    },
    {
        "title": "Yapı Kredi Bankası",
        "description": "Yapı Kredi Bankası or simply Yapı Kredi is Turkey's third largest private bank.",
        "url": "https://www.yapikredi.com.tr/",
    },
    {
        "title": "Etrade",
        "description": "Etrade is an exchange.",
        "url": "https://www.etrade.com/",
    },
    {
        "title": "Midas",
        "description": "Midas is an exchange.",
        "url": "https://www.getmidas.com/",
    },
    {
        "title": "Binance",
        "description": "Binance is a cryptocurrency exchange that provides a platform for trading various cryptocurrencies.",
        "url": "https://www.binance.com/",
    },
    {
        "title": "Coinbase",
        "description": "Coinbase is a digital currency exchange headquartered in San Francisco, California, United States.",
        "url": "https://www.coinbase.com/",
    },
    {
        "title": "Paribu",
        "description": "Paribu is a Turkish cryptocurrency exchange.",
        "url": "https://www.paribu.com/",
    },
    {
        "title": "Icrypex",
        "description": "Icrypex is a Turkish cryptocurrency exchange.",
        "url": "https://www.icrypex.com/",
    },
]

for platform in PLATFORMS:
    response = requests.post(
        API_URL + "platform",
        json=platform,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    if response.ok:
        print(f"{response.status_code}: {platform['title']} created successfully")


# create markets
MARKETS = [
    {"title": "Borsa İstanbul", "code": "BIST", "currency_code": "TRY"},
    {
        "title": "The NASDAQ Global Select Market",
        "code": "NASDAQGS",
        "currency_code": "USD",
    },
    {"title": "New York Stock Exchange", "code": "NYSE", "currency_code": "USD"},
    {"title": "Crypto Currency Exchange", "code": "CRYPTO", "currency_code": "USDT"},
    {"title": "Crypto Currency Exchange", "code": "CRYPTO", "currency_code": "TRY"},
    {"title": "Other OTC", "code": "OTC", "currency_code": "USD"},
]

for market in MARKETS:
    response = requests.post(
        API_URL + "market",
        json=market,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    if response.ok:
        print(f"{response.status_code}: {market['code']} created successfully")


# create tickers
TICKERS = [
    {
        "code": "BCS",
        "title": "Barclays PLC",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://home.barclays/",
    },
    {
        "title": "Udemy, Inc.",
        "code": "UDMY",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.udemy.com/",
    },
    {
        "title": "Apple Inc.",
        "code": "AAPL",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.apple.com/",
    },
    {
        "title": "NVIDIA Corporation",
        "code": "NVDA",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.nvidia.com/",
    },
    {
        "title": "Uber Technologies, Inc.",
        "code": "UBER",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.uber.com/",
    },
    {
        "title": "Skechers U.S.A., Inc.",
        "code": "SKX",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.skechers.com/",
    },
    {
        "title": "Starbucks Corporation",
        "code": "SBUX",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.starbucks.com/",
    },
    {
        "title": "Virgin Galactic Holdings, Inc.",
        "code": "SPCE",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.virgingalactic.com/",
    },
    {
        "title": "Chegg, Inc.",
        "code": "CHGG",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.chegg.com/",
    },
    {
        "title": "WeWork Inc.",
        "code": "WEWKQ",
        "market_code": "OTC",
        "currency_code": "USD",
        "url": "https://www.wework.com/",
    },
    {
        "title": "Snap Inc.",
        "code": "SNAP",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.snap.com/",
    },
    {
        "code": "NFLX",
        "title": "Netflix, Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.netflix.com/",
    },
    {
        "code": "TDOC",
        "title": "Teladoc Health, Inc.",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.teladochealth.com/",
    },
    {
        "code": "SLDP",
        "title": "Solid Power, Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.solidpowerbattery.com/",
    },
    {
        "code": "VORBQ",
        "title": "Virgin Orbit, Inc.",
        "market_code": "OTC",
        "currency_code": "USD",
        "url": "https://www.virginorbit.com/",
    },
    {
        "code": "AI",
        "title": "C3.ai, Inc.",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://c3.ai/",
    },
    {
        "code": "BABA",
        "title": "Alibaba Group Holding Limited",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.alibabagroup.com/",
    },
    {
        "code": "GOOG",
        "title": "Alphabet Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://abc.xyz/",
    },
    {
        "code": "TSLA",
        "title": "Tesla, Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.tesla.com/",
    },
    {
        "code": "AMD",
        "title": "Advanced Micro Devices, Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.amd.com/",
    },
    {
        "code": "TSM",
        "title": "Taiwan Semiconductor Manufacturing Company Limited",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.tsmc.com/",
    },
    {
        "code": "RXRX",
        "title": "Recursion Pharmaceuticals, Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.recursion.com/",
    },
    {
        "code": "ARM",
        "title": "Arm Holdings plc",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.arm.com/",
    },
    {
        "code": "PEP",
        "title": "PepsiCo, Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.pepsico.com/",
    },
    {
        "code": "F",
        "title": "Ford Motor Company",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.ford.com/",
    },
    {
        "code": "ORCL",
        "title": "Oracle Corporation",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.oracle.com/",
    },
    {
        "code": "BMBL",
        "title": "Bumble Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://bumble.com/",
    },
    {
        "code": "NKE",
        "title": "NIKE, Inc.",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.nike.com/",
    },
    {
        "code": "GLCVY",
        "title": "Gelecek Varlik Yonetimi AS",
        "market_code": "BIST",
        "currency_code": "TRY",
    },
    {
        "code": "ADA",
        "title": "Cardano",
        "market_code": "Crypto",
        "currency_code": "USDT",
        "url": "https://cardano.org/",
    },
    {
        "code": "ADA",
        "title": "Cardano",
        "market_code": "Crypto",
        "currency_code": "TRY",
        "url": "https://cardano.org/",
    },
    {
        "code": "GAU",
        "title": "Gamer Arena Utility Token",
        "market_code": "Crypto",
        "currency_code": "TRY",
        "url": "https://gamerarena.com/",
    },
    {
        "code": "DAL",
        "title": "Delta Air Lines, Inc.",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.delta.com/",
    },
    {
        "code": "SHOP",
        "title": "Shopify Inc.",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.shopify.com/",
    },
    {
        "code": "ABNB",
        "title": "Airbnb, Inc.",
        "market_code": "NASDAQGS",
        "currency_code": "USD",
        "url": "https://www.airbnb.com/",
    },
    {
        "code": "ONON",
        "title": "On Holding AG",
        "market_code": "NYSE",
        "currency_code": "USD",
        "url": "https://www.on-running.com/",
    },
]

for ticker in TICKERS:
    response = requests.post(
        API_URL + "ticker",
        json=ticker,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    if response.ok:
        print(f"{response.status_code}: {ticker['code']} created successfully")
