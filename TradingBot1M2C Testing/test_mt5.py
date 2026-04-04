import MetaTrader5 as mt5

# ── Config ทดสอบ — แก้ตามพอร์ต Demo ────────────────────────
SYMBOL = "XAUUSD"  # เปลี่ยนให้ตรงกับ Symbol ใน MT5
LOT = 0.01  # Lot เล็กสุดสำหรับทดสอบ

if not mt5.initialize():
    print(f"❌ เชื่อมต่อไม่ได้: {mt5.last_error()}")
    exit()

# ดึงราคาปัจจุบัน
tick = mt5.symbol_info_tick(SYMBOL)
if tick is None:
    print(f"❌ ดึงราคา {SYMBOL} ไม่ได้ — ตรวจสอบชื่อ Symbol")
    mt5.shutdown()
    exit()

ask = tick.ask
bid = tick.bid
print(f"✅ ราคาปัจจุบัน  Ask={ask}  Bid={bid}")

# คำนวณ Entry / SL / TP จำลอง
# Buy Stop ที่ Ask + 50 pips, SL = Ask - 50 pips, TP = Ask + 75 pips
pip = mt5.symbol_info(SYMBOL).point * 10
entry = round(ask + pip * 50, 2)
sl = round(ask - pip * 50, 2)
tp = round(ask + pip * 75, 2)

print(f"   Entry={entry}  SL={sl}  TP={tp}")

# ส่ง Buy Stop Order
request = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": SYMBOL,
    "volume": LOT,
    "type": mt5.ORDER_TYPE_BUY_STOP,
    "price": entry,
    "sl": sl,
    "tp": tp,
    "magic": 20250101,
    "comment": "test_1M2C",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

result = mt5.order_send(request)

if result.retcode == mt5.TRADE_RETCODE_DONE:
    print(f"✅ Order สำเร็จ! Ticket={result.order}")
    print(f"   ดู Order ใน MT5 → Trade tab")
else:
    print(f"❌ Order ล้มเหลว: retcode={result.retcode}")
    print(f"   {result.comment}")

mt5.shutdown()
