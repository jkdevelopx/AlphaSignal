import sqlite3
import pandas as pd
import requests
from datetime import datetime

TOKEN = "8540357764:AAGMtyaYL9jLWVDA24LSGvIjIa92oE8QiFY"
# หา CHAT_ID โดยส่งข้อความไปที่ bot ก่อน แล้ว forward ไป @userinfobot
# หรือลองส่งข้อความทดสอบก่อน ถ้าไม่ขึ้นแปลว่า CHAT_ID ผิด
# ตอนนี้ผมใส่ให้ก่อน (ถ้าไม่ขึ้นให้บอกผม เดี๋ยวช่วยหา)
CHAT_ID = "7518743348"  # แก้เป็นของคุณจริง ๆ ถ้าต้องการ

db = "data/portfolio.db"
conn = sqlite3.connect(db)
df = pd.read_sql("""
    SELECT symbol, close, date FROM price_data 
    WHERE date = (SELECT MAX(date) FROM price_data)
    ORDER BY symbol
""", conn)
conn.close()

# คำนวณ % เปลี่ยนจากเมื่อวาน (ถ้ามีข้อมูล)
signals = []
for sym in df['symbol'].unique():
    data = pd.read_sql(f"SELECT date, close FROM price_data WHERE symbol='{sym}' ORDER BY date DESC LIMIT 2", conn)
    if len(data) == 2:
        change = (data.iloc[0]['close'] - data.iloc[1]['close']) / data.iloc[1]['close'] * 100
        emoji = "Buy" if change > 1.5 else "Sell" if change < -1.5 else "Hold"
        signals.append(f"{emoji} **{sym}** {data.iloc[0]['close']:.2f} ({change:+.2f}%)")
    else:
        signals.append(f"Hold **{sym}** {data.iloc[0]['close']:.2f}")

message = f"*AlphaSignal Portfolio Update*\n{datetime.now().strftime('%Y-%m-%d %H:%M')} (TH)\n\n"
message += "\n".join(signals[:16])  # 16 ตัวของคุณ
message += f"\n\n#AlphaSignal #Portfolio"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})

print("Telegram sent to portfolio group!")
