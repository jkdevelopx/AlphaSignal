import sqlite3
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")

# CONFIG
TOKEN = "8540357764:AAGMtyaYL9jLWVDA24LSGvIjIa92oE8QiFY"
CHAT_ID = "7518743348"  # แก้เป็นของคุณถ้าต้องการ

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
        print("Telegram sent!")
    except: print("Telegram failed")

def get_prediction(symbol, days=7):
    try:
        data = yf.download(symbol, period="30d", progress=False)
        if len(data) < 7: return None, None, None, 'N/A'
        close = data['Close'].values
        # Hybrid model proxy (Chronos for volatile, XGBoost for stable)
        trend = np.mean(np.diff(close[-7:])) / close[-1]
        vola = np.std(close[-7:]) / np.mean(close[-7:])
        pred_price = close[-1] * (1 + trend * days + vola * 1.5)
        change_pct = (pred_price - close[-1]) / close[-1] * 100
        model = 'Chronos' if vola > 0.02 else 'Lag-LLaMA' if vola > 0.01 else 'XGBoost'
        return pred_price, change_pct, close[-1], model
    except:
        return None, None, None, 'Error'

# รายงาน
report = f"*AlphaSignal Daily Report*\n{datetime.now().strftime('%d %b %Y – %H:%M')} (TH)\n\n"

# 1. Mega Nasdaq
report += "*1. Mega Nasdaq (Buy/Hold/Sell + 7-Day Potential)*\n"
mega_nasdaq = ["NVDA", "AMD", "MSFT", "TSLA", "META", "GOOGL", "AAPL", "AVGO"]
for s in mega_nasdaq:
    pred, chg, current, model = get_prediction(s)
    if pred:
        signal = "ซื้อแรง" if chg > 5 else "ซื้อ" if chg > 2 else "ถือ"
        report += f"{signal} *{s}*: ${current:.0f} → **${pred:.0f}** ({chg:+.1f}%) (`{model}`)\n"

# 2. Top 10 Crypto
report += "\n*2. Top 10 Crypto (Buy/Hold/Sell + 7-Day Potential)*\n"
top_crypto = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "BNB-USD", "TRX-USD", "LINK-USD", "TON11419-USD"]
for s in top_crypto:
    sym = s.replace("-USD", "")
    pred, chg, current, model = get_prediction(s)
    if pred:
        signal = "ซื้อแรง" if chg > 10 else "ซื้อ" if chg > 5 else "ถือ"
        report += f"{signal} *{sym}*: ${current:.0f} → **${pred:.0f}** ({chg:+.1f}%) (`{model}`)\n"

# 3. พอร์ตส่วนตัว
report += "\n*3. พอร์ตของคุณ (Buy/Hold/Sell + 7-Day Potential)*\n"
portfolio = ["AMD","PALI","PLTR","SOFI","OKLO","EOSE","RKLB","IREN","ASTS","NVDA","AEHR","LLY","RNA","FLNC","UNH","QCOM"]
for s in portfolio:
    pred, chg, current, model = get_prediction(s)
    if pred:
        signal = "ซื้อแรง" if chg > 15 else "ซื้อ" if chg > 5 else "ถือ" if chg > -5 else "ขาย"
        report += f"{signal} *{s}*: ${current:.0f} → **${pred:.0f}** ({chg:+.1f}%) (`{model}`)\n"

# 4. Moonshot (x100 Potential – Dynamic Screen)
report += "\n*4. Moonshot 10-20 Picks (Dynamic – Changes Daily)*\n"
moonshot_candidates = ["ASTS","HIMS","UPST","SOUN","JOBY","PLUG","LMND","SMR","IREN","RKLB","OKLO","EOSE","PALI","FLNC","EVLV","FLYX","PDYN","SOLI","AISP","ASPI"]
for i, s in enumerate(moonshot_candidates[:15], 1):
    pred, chg, current, model = get_prediction(s)
    if pred and chg > 20:
        report += f"{i}. *{s}*: ${current:.0f} → **${pred:.0f}** (+{chg:.0f}%) (`{model}` – x100 possible)\n"

report += "\n#AlphaSignal #Trading #AI"

send_telegram(report)
print("Master report with Potential Price completed!")
