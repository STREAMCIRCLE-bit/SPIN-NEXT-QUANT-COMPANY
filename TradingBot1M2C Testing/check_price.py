import MetaTrader5 as mt5

mt5.initialize()
symbol = "XAUUSD"
tick = mt5.symbol_info_tick(symbol)
info = mt5.symbol_info(symbol)

print(f"Ask       = {tick.ask}")
print(f"Bid       = {tick.bid}")
print(f"StopLevel = {info.trade_stops_level} points")
print(f"Point     = {info.point}")
print(f"Min Stop  = {info.trade_stops_level * info.point:.2f}")

mt5.shutdown()
