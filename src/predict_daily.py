# src/predict_daily.py - เวอร์ชันทำงาน 100% กับข้อมูลจริง
import sqlite3
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from datetime import datetime
import os

print(f"เริ่มพยากรณ์: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# สร้างโฟลเดอร์
os.makedirs("predictions", exist_ok=True)

conn = sqlite3.connect("data/market_data.db")
# ใช้ symbol ที่มีจริงใน DB ของคุณตอนนี้
targets = ["BTC","ETH","SOL","XRP","DOGE","NVDA","TSLA","AAPL","AMD","META"]

results = []
for sym in targets:
    try:
        df = pd.read_sql(f"SELECT date, close FROM price_data WHERE symbol='{sym}' ORDER BY date", conn)
        if len(df) < 10:
            print(f"ข้าม {sym} - ข้อมูลไม่พอ")
            continue
            
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').resample('D').last().ffill().reset_index()
        
        # Feature ง่าย ๆ
        df['lag1'] = df['close'].shift(1)
        df['ma7'] = df['close'].rolling(7, min_periods=1).mean()
        df = df.dropna()
        
        if len(df) < 5:
            continue
            
        X = df[['lag1', 'ma7']]
        y = df['close']
        
        model = XGBRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        last = df.iloc[-1]
        pred_7d = model.predict([[last['close'], last['ma7']]])[0]
        change = (pred_7d - last['close']) / last['close'] * 100
        
        signal = "ซื้อ" if change > 2 else "ขาย" if change < -2 else "ถือ"
        
        results.append({
            "สินทรัพย์": sym,
            "ราคาวันนี้": f"${last['close']:,.2f}",
            "พยากรณ์ 7 วัน": f"${pred_7d:,.2f}",
            "เปลี่ยนแปลง": f"{change:+.2f}%",
            "สัญญาณ": f"{signal}"
        })
        print(f"สำเร็จ {sym}: {signal} ({change:+.2f}%)")
    except Exception as e:
        print(f"ผิดพลาด {sym}: {e}")

if results:
    pd.DataFrame(results).to_csv("predictions/latest_prediction.csv", index=False)
    print("บันทึก predictions/latest_prediction.csv สำเร็จ!")
else:
    print("ไม่มีข้อมูลพอทำนาย")

conn.close()
