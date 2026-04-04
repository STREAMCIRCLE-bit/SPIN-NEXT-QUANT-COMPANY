# 1M2C Webhook Server

Flask รับสัญญาณจาก TradingView → ส่งคำสั่งไป MetaTrader 5

## โครงสร้างไฟล์

```
flask_webhook/
  app.py            ← Flask Server + Event Router
  mt5_handler.py    ← MT5 functions
  order_store.py    ← State ของ Order ใน memory
  requirements.txt
  README.md
```

## ขั้นตอนติดตั้ง (Windows เท่านั้น)

### 1. ติดตั้ง Python dependencies
```bash
pip install -r requirements.txt
```

### 2. เปิด MT5 Terminal และ Login
- เปิด MetaTrader 5
- Login เข้า Account ที่ต้องการ
- ไปที่ Tools → Options → Expert Advisors
- เปิด "Allow algorithmic trading"

### 3. รัน Flask Server
```bash
python app.py
```
เห็น output: `Flask Webhook Server เริ่มทำงาน  port=5000`

### 4. รัน ngrok (Terminal ใหม่)
```bash
ngrok http 5000
```
จะได้ URL เช่น `https://abc123.ngrok-free.app`

### 5. ใส่ URL ใน TradingView Alert
```
Webhook URL: https://abc123.ngrok-free.app/alert
```

## ทดสอบด้วย curl

### ทดสอบ health check
```bash
curl http://localhost:5000/health
```

### จำลอง order_confirmed (Buy)
```bash
curl -X POST http://localhost:5000/alert \
  -H "Content-Type: application/json" \
  -d '{
    "event": "order_confirmed",
    "side": "buy",
    "symbol": "XAUUSD",
    "timeframe": "240",
    "signal_id": 1000,
    "entry_high": 2345.50,
    "entry_low": 2320.00,
    "lot": 0.15,
    "reward_1r": 2371.00,
    "reward_1_5r": 2383.25
  }'
```

### ดู State ของ Order ทั้งหมด
```bash
curl http://localhost:5000/orders
```

## Event Summary

| Event | Pine ส่งเมื่อ | Flask ทำอะไร |
|-------|-------------|-------------|
| signal_new | Pattern เจอ (ยังไม่ปิดแท่ง) | Log ไว้ |
| pre_warning | 10 นาทีก่อนปิดแท่ง | Log ไว้ |
| order_confirmed | แท่งปิดยืนยัน | วาง Pending Stop Order MT5 |
| order_filled | ราคาชน Entry | อัปเดต State → active |
| cancel_pending | ราคาชน SL ก่อน Fill | Cancel Pending Order MT5 |
| breakeven | ราคาถึง 1R | เลื่อน SL → Entry ใน MT5 |

## State Transitions

```
(Pine: order_confirmed)
        ↓
    PENDING
     ↙     ↘
(order_filled) (cancel_pending)
    ↓               ↓
  ACTIVE        CANCELLED
    ↓
(breakeven)
    ↓
 BREAKEVEN
    ↓
(MT5 ปิด TP หรือ SL เอง)
    ↓
  CLOSED
```
