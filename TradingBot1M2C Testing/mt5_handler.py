import logging
from typing import Optional
import MetaTrader5 as mt5

log = logging.getLogger(__name__)
MAGIC_NUMBER = 20250101


def _connect() -> bool:
    if not mt5.initialize():
        log.error(f"MT5 initialize() failed: {mt5.last_error()}")
        return False
    return True


def place_pending_order(
    symbol: str,
    side: str,
    entry: float,
    sl: float,
    tp: float,
    lot: float,
    comment: str = "",
) -> Optional[int]:
    if not _connect():
        return None

    order_type = mt5.ORDER_TYPE_BUY_STOP if side == "buy" else mt5.ORDER_TYPE_SELL_STOP

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": entry,
        "sl": sl,
        "tp": tp,
        "magic": MAGIC_NUMBER,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        retcode = result.retcode if result else "None"
        comment_str = result.comment if result else "no result"
        log.error(f"place_pending_order failed: retcode={retcode}  {mt5.last_error()}")
        log.error(f"  comment : {comment_str}")
        log.error(f"  request : {request}")
        return None

    log.info(
        f"place_pending_order OK: ticket={result.order}  {side.upper()} {symbol}  lot={lot}"
    )
    return result.order


def cancel_pending_order(ticket: int) -> bool:
    if not _connect():
        return False

    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket,
    }

    result = mt5.order_send(request)

    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        retcode = result.retcode if result else "None"
        log.error(f"cancel_pending_order failed: ticket={ticket}  retcode={retcode}")
        return False

    log.info(f"cancel_pending_order OK: ticket={ticket}")
    return True


def move_sl_to_breakeven(ticket: int, new_sl: float) -> bool:
    if not _connect():
        return False

    positions = mt5.positions_get(ticket=ticket)
    if not positions:
        log.error(f"move_sl_to_breakeven: position not found ticket={ticket}")
        return False

    pos = positions[0]

    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": pos.symbol,
        "position": ticket,
        "sl": new_sl,
        "tp": pos.tp,
    }

    result = mt5.order_send(request)

    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        retcode = result.retcode if result else "None"
        log.error(f"move_sl_to_breakeven failed: ticket={ticket}  retcode={retcode}")
        return False

    log.info(f"move_sl_to_breakeven OK: ticket={ticket}  SL -> {new_sl}")
    return True
