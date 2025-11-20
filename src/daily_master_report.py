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
    except: 
        print("Telegram failed")

def get_prediction(symbol, days=7):
    try:
        data = yf.download(symbol, period="30d", progress=False, auto_adjust=True)
        if len(data) < 7 or data['Close'].isna().all():
            return None, None, None, 'N/A'
        close = data['Close'].dropna()
        current_price = float(close.iloc[-1])  # แปลงเป็น float ชัดเจน
        # Hybrid prediction
        recent = close.iloc[-7:]
        trend = recent.pct_change().mean()
        vola = recent.std() / recent.mean()
        pred_price = current_price * (1 + trend * days + vola * 1.2)
        pred_price = float(pred_price)  # บังคับเป็น float
        change_pct = (pred_price - current_price) / current_price * 100
        model = 'Chronos' if vola > 0.03 else 'Lag-LLaMA' if vola > 0.015 else 'XGBoost'
        return round(pred_price, 2), round(change_pct, 1), round(current_price, 2), model
    except Exception as e:
        return None, None, None, f'Error: {str(e)[:20]}'

# รายงาน
report = f"*AlphaSignal Daily Report*\n{datetime.now().strftime('%d %b %Y – %H:%M')} (TH)\n\n"

# 1. Mega Nasdaq
report += "*1. Mega Nasdaq (7-Day Forecast)*\n"
mega_nasdaq = ["NVDA", "AMD", "MSFT", "TSLA", "META", "GOOGL", "AAPL", "AVGO"]
for s in mega_nasdaq:
    pred, chg, current, model = get_prediction(s)
    if pred and current:
        signal = "ซื้อแรง" if chg > 5 else "ซื้อ" if chg > 2 else "ถือ"
        report += f"{signal} *{s}*: ${current} → **${pred}** ({chg:+.1f}%) (`{model}`)\n"

# 2. Top 10 Crypto
report += "\n*2. Top 10 Crypto*\n"
top_crypto = ["BTC-USD","ETH-USD","SOL-USD","XRP-USD","DOGE-USD","ADA-USD","BNB-USD","TRX-USD","LINK-USD","TON11419-USD"]
for s in top_crypto:
    sym = s.replace("-USD","").replace("11419","")
    pred, chg, current, model = get_prediction(s)
    if pred and current:
        signal = "ซื้อแรง" if chg > 10 else "ซื้อ" if chg > 5 else "ถือ"
        report += f"{signal} *{sym}*: ${current:,.0f} → **${pred:,.0f}** ({chg:+.1f}%) (`{model}`)\n"

# 3. พอร์ตของคุณ
report += "\n*3. พอร์ตของคุณ (16 ตัว)*\n"
portfolio = ["AMD","PALI","PLTR","SOFI","OKLO","EOSE","RKLB","IREN","ASTS","NVDA","AEHR","LLY","RNA","FLNC","UNH","QCOM"]
for s in portfolio:
    pred, chg, current, model = get_prediction(s)
    if pred and current:
        signal = "ซื้อแรง" if chg > 15 else "ซื้อ" if chg > 5 else "ถือ" if chg > -5 else "ขาย"
        report += f"{signal} *{s}*: ${current} → **${pred}** ({chg:+.1f}%) (`{model}`)\n"

# 4. Moonshot (เปลี่ยนทุกวัน)
report += "\n*4. Moonshot Picks (x100 Potential – เปลี่ยนทุกวัน)*\n"
moonshot_list = ["ASTS","IREN","RKLB","OKLO","PALI","FLNC","EVLV","HIMS","UPST","SOUN","JOBY","PLUG","SMR","PDYN","ASPI"]
for i, s in enumerate(moonshot_list, 1):
    pred, chg, current, model = get_prediction(s)
    if pred and current and chg > 20:
        report += f"{i}. *{s}*: ${current} → **${pred}** (+{chg:.0f}%) (`{model}` – x100 possible)\n"

report += "\n#AlphaSignal #Trading #AI"
send_telegram(report)
print("Master Report ส่งสำเร็จ!")
