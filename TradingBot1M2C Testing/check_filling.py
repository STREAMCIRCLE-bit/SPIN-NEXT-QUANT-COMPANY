import MetaTrader5 as mt5

mt5.initialize()
info = mt5.symbol_info("XAUUSD")

filling = info.filling_mode
print(f"Filling mode: {filling}")
print(f"  FOK    (1): {'รองรับ' if filling & 1 else 'ไม่รองรับ'}")
print(f"  IOC    (2): {'รองรับ' if filling & 2 else 'ไม่รองรับ'}")
print(f"  RETURN (4): {'รองรับ' if filling & 4 else 'ไม่รองรับ'}")

mt5.shutdown()