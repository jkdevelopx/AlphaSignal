import yfinance as yf
import pandas as pd
import sqlite3
import os
from datetime import datetime
import time

print(f"Starting Portfolio ETL: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

os.makedirs("data", exist_ok=True)
db_path = "data/portfolio.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS price_data (
    symbol TEXT, date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL,
    PRIMARY KEY (symbol, date)
)''')

# Your portfolio stocks
portfolio = ["AMD", "PALI", "PLTR", "SOFI", "OKLO", "EOSE", "RKLB", "IREN", "ASTS", "NVDA", "AEHR", "LLY", "RNA", "FLNC", "UNH", "QCOM"]

print("Fetching portfolio data (90 days)...")
for s in portfolio:
    try:
        df = yf.download(s, period="90d", interval="1d", progress=False)
        for idx, row in df.iterrows():
            c.execute("INSERT OR REPLACE INTO price_data VALUES (?,?,?,?,?,?,?)",
                     (s, str(idx.date()), float(row['Open']), float(row['High']),
                      float(row['Low']), float(row['Close']), float(row['Volume'])))
        print(f"  {s} → {len(df)} days")
        time.sleep(0.2)
    except Exception as e:
        print(f"  Error {s}: {e}")

conn.commit()
conn.close()
print(f"Portfolio ETL done! Saved to {db_path} (size: {os.path.getsize(db_path)/1024/1024:.1f} MB)")
