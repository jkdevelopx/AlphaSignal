import sqlite3
import pandas as pd
import requests
from datetime import datetime

TOKEN = "8540357764:AAGMtyaYL9jLWVDA24LSGvIjIa92oE8QiFY"
# ใส่ CHAT_ID ของคุณจริง ๆ ที่ได้จาก @userinfobot
CHAT_ID = "123456789"  # แก้เป็นเลขจริงของคุณที่นี่ด้วยนะครับ

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print("Telegram sent successfully!")
    except Exception as e:
        print(f"Telegram failed: {e}")

# เปิด connection ครั้งเดียว
db_path = "data/portfolio.db"
conn = sqlite3.connect(db_path)

# ดึงข้อมูลล่าสุดของทุกตัว
query = """
SELECT symbol, close, date 
FROM price_data 
WHERE date = (SELECT MAX(date) FROM price_data WHERE symbol = price_data.symbol)
ORDER BY symbol
"""
latest = pd.read_sql(query, conn)

# สร้างข้อความ
message = f"*AlphaSignal Portfolio Update*\n{datetime.now().strftime('%d %b %Y – %H:%M')} (TH)\n\n"

for _, row in latest.iterrows():
    sym = row['symbol']
    price = row['close']
    
    # ดึงราคาเมื่อวาน (2 วันล่าสุด)
    hist = pd.read_sql(f"""
        SELECT close FROM price_data 
        WHERE symbol = '{sym}' 
        ORDER BY date DESC LIMIT 2
    """, conn)
    
    if len(hist) == 2:
        change = (hist.iloc[0]['close'] - hist.iloc[1]['close']) / hist.iloc[1]['close'] * 100
        emoji = "Buy" if change > 2 else "Sell" if change < -2 else "Hold"
        message += f"{emoji} *{sym}* `${price:.3f}` ({change:+.2f}%)\n"
    else:
        message += f"Hold *{sym}* `${price:.3f}`\n"

message += "\n#AlphaSignal #Portfolio"

# ปิด connection หลังใช้เสร็จ
conn.close()

send_telegram(message)
