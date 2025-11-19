import yfinance as yf
import ccxt
import pandas as pd
import sqlite3
import os
from datetime import datetime
import time

print(f"ETL ย้อนหลัง 90 วัน - เริ่ม {datetime.now().strftime('%H:%M')}")

os.makedirs("data", exist_ok=True)
db_path = "data/market_data.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS price_data (
    symbol TEXT, date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL,
    PRIMARY KEY (symbol, date)
)''')

# ดึงหุ้นย้อนหลัง 90 วัน
stocks = ["AAPL","MSFT","NVDA","TSLA","AMD","META","AMZN","GOOGL","INTC","NFLX"]
print("ดึงหุ้นย้อนหลัง 90 วัน...")
for s in stocks:
    try:
        df = yf.download(s, period="90d", interval="1d", progress=False)
        for idx, row in df.iterrows():
            c.execute("INSERT OR IGNORE INTO price_data VALUES (?,?,?,?,?,?,?)",
                     (s, str(idx.date()), float(row['Open']), float(row['High']),
                      float(row['Low']), float(row['Close']), float(row['Volume'])))
        print(f"  {s} → {len(df)} วัน")
        time.sleep(0.2)
    except: pass

# ดึงคริปโตย้อนหลัง 90 วัน
exchange = ccxt.binance()
crypto = ["BTC/USDT","ETH/USDT","SOL/USDT","XRP/USDT","DOGE/USDT"]
print("ดึงคริปโตย้อนหลัง 90 วัน...")
for sym in crypto:
    try:
        ohlcv = exchange.fetch_ohlcv(sym, timeframe='1d', limit=90)
        for item in ohlcv:
            ts, o, h, l, cl, v = item
            date_str = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d')
            coin = sym.split('/')[0]
            c.execute("INSERT OR IGNORE INTO price_data VALUES (?,?,?,?,?,?,?)",
                     (coin, date_str, o, h, l, cl, v))
        print(f"  {coin} → {len(ohlcv)} วัน")
        time.sleep(0.3)
    except Exception as e:
        print(f"  {sym} error: {e}")

conn.commit()
conn.close()
print(f"ETL เสร็จ! DB มีข้อมูลย้อนหลัง 90 วันเรียบร้อย")
print(f"ขนาด: {os.path.getsize(db_path)/1024/1024:.1f} MB")
