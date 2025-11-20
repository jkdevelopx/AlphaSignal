import sqlite3
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from datetime import datetime
import os

# Chronos
try:
    from chronos import ChronosPipeline
    chronos = ChronosPipeline.from_pretrained("amazon/chronos-t5-small", device_map="cpu")
    CHRONOS_AVAILABLE = True
except:
    CHRONOS_AVAILABLE = False

print(f"เริ่มพยากรณ์ Chronos: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

os.makedirs("predictions", exist_ok=True)
conn = sqlite3.connect("data/market_data.db")
targets = ["BTC", "ETH", "SOL", "XRP", "DOGE", "NVDA", "TSLA", "AAPL", "AMD", "META"]

results = []
for sym in targets:
    try:
        df = pd.read_sql(f"SELECT date, close FROM price_data WHERE symbol='{sym}' ORDER BY date", conn)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').resample('D').last().ffill().reset_index()
        series = df['close'].dropna().values

        if len(series) < 30:
            print(f"ข้าม {sym} - ข้อมูลไม่พอ")
            continue

        last_price = series[-1]
        if sym in ["BTC", "ETH", "SOL"]:  # Chronos สำหรับคริปโต
            if CHRONOS_AVAILABLE:
                input_series = np.array(series[-30:], dtype=np.float32)
                forecast = chronos.predict([input_series], prediction_length=7)
                pred_7d = forecast[0].mean.numpy()[-1]
            else:
                pred_7d = last_price * 1.02  # Fallback
        else:  # XGBoost สำหรับหุ้น
            df_xgb = df.copy()
            df_xgb['lag1'] = df_xgb['close'].shift(1)
            df_xgb['ma7'] = df_xgb['close'].rolling(7).mean()
            df_xgb = df_xgb.dropna()
            X = df_xgb[['lag1', 'ma7']]
            y = df_xgb['close']
            model = XGBRegressor(n_estimators=100)
            model.fit(X, y)
            last = df_xgb.iloc[-1]
            pred_7d = model.predict([[last['close'], last['ma7']]])[0]

        change = (pred_7d - last_price) / last_price * 100
        signal = "ซื้อ" if change > 2 else "ขาย" if change < -2 else "ถือ"

        results.append({
            "สินทรัพย์": sym,
            "ราคาวันนี้": f"${last_price:,.2f}",
            "พยากรณ์ 7 วัน": f"${pred_7d:,.2f}",
            "เปลี่ยนแปลง": f"{change:+.2f}%",
            "สัญญาณ": signal
        })
        print(f"{sym}: {signal} ({change:+.2f}%)")
    except Exception as e:
        print(f"ผิดพลาด {sym}: {e}")

conn.close()
if results:
    pd.DataFrame(results).to_csv("predictions/latest_prediction.csv", index=False)
    print("บันทึก predictions/latest_prediction.csv สำเร็จ!")
