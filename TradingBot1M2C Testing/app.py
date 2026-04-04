"""
Flask Webhook Server — รับสัญญาณจาก TradingView แล้วส่งคำสั่งไป MT5
สัมพันธ์กับ Pine Script: 1M2C_webhook_v3.pine

Event ที่รับได้:
  signal_new       → Log ไว้เฉยๆ (แท่งยังไม่ปิด)
  pre_warning      → Log ไว้เฉยๆ (10 นาทีก่อนปิด)
  order_confirmed  → วาง Pending Stop Order ใน MT5
  order_filled     → อัปเดต State เป็น Active
  cancel_pending   → Cancel Pending Order ใน MT5
  breakeven        → เลื่อน SL มาที่ Entry ใน MT5

โครงสร้างไฟล์:
  app.py           ← ไฟล์นี้ (Flask + Event Router)
  mt5_handler.py   ← MT5 functions (วาง/Cancel/แก้ Order)
  order_store.py   ← เก็บ State ของ Order แต่ละ signal_id
  requirements.txt ← dependencies
"""

import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

from order_store import OrderStore
from mt5_handler import (
    place_pending_order,
    cancel_pending_order,
    move_sl_to_breakeven,
)

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── App & Store ──────────────────────────────────────────────────────────────
app = Flask(__name__)
store = OrderStore()  # เก็บ State ทุก Order ใน memory (dict)


# ════════════════════════════════════════════════════════════════════════════
# WEBHOOK ENDPOINT
# ════════════════════════════════════════════════════════════════════════════
@app.route("/alert", methods=["POST"])
def alert():
    """
    รับ JSON payload จาก TradingView แล้ว route ตาม event
    TradingView ส่ง Content-Type: application/json
    """

    # ── Parse JSON ──────────────────────────────────────────────────────────
    try:
        data = request.get_json(force=True)
        if not data:
            raise ValueError("Empty body")
    except Exception as e:
        log.error(f"Parse error: {e}  raw={request.data[:200]}")
        return jsonify({"status": "error", "msg": "invalid json"}), 400

    event = data.get("event", "")
    symbol = data.get("symbol", "")
    signal_id = data.get("signal_id")  # bar_index ของแท่งแม่ (int)
    side = data.get("side", "")  # "buy" หรือ "sell"

    log.info(
        f"[RECV] event={event}  symbol={symbol}  signal_id={signal_id}  side={side}"
    )

    # ── Route ตาม event ─────────────────────────────────────────────────────
    if event == "signal_new":
        return handle_signal_new(data)

    elif event == "pre_warning":
        return handle_pre_warning(data)

    elif event == "order_confirmed":
        return handle_order_confirmed(data)

    elif event == "order_filled":
        return handle_order_filled(data)

    elif event == "cancel_pending":
        return handle_cancel_pending(data)

    elif event == "breakeven":
        return handle_breakeven(data)

    else:
        log.warning(f"Unknown event: {event}")
        return jsonify({"status": "ignored", "msg": f"unknown event: {event}"}), 200


# ════════════════════════════════════════════════════════════════════════════
# EVENT HANDLERS
# ════════════════════════════════════════════════════════════════════════════


def handle_signal_new(data: dict):
    """
    แท่งยังไม่ปิด — Log ไว้เฉยๆ รอ order_confirmed
    ไม่ส่งอะไรไป MT5
    """
    log.info(
        f"  [signal_new] {data['side'].upper()} {data['symbol']}  "
        f"H={data['entry_high']}  L={data['entry_low']}  lot={data['lot']}"
    )
    return jsonify({"status": "ok", "msg": "logged"}), 200


def handle_pre_warning(data: dict):
    """
    10 นาทีก่อนปิดแท่ง — Log ไว้ อาจส่ง Line/Telegram แจ้งเตือนได้ในอนาคต
    ไม่ส่งอะไรไป MT5
    """
    log.info(
        f"  [pre_warning] {data['side'].upper()} {data['symbol']}  "
        f"เหลือ 10 นาที  H={data['entry_high']}  L={data['entry_low']}"
    )
    return jsonify({"status": "ok", "msg": "logged"}), 200


def handle_order_confirmed(data: dict):
    """
    แท่งปิดยืนยัน → วาง Pending Stop Order ใน MT5

    Buy Stop:   Entry=entry_high  SL=entry_low   TP=reward_1_5r
    Sell Stop:  Entry=entry_low   SL=entry_high  TP=reward_1_5r
    """
    signal_id = data["signal_id"]
    side = data["side"]
    symbol = data["symbol"]
    entry_high = float(data["entry_high"])
    entry_low = float(data["entry_low"])
    lot = float(data["lot"])
    tp = float(data["reward_1_5r"])  # TP คงที่ที่ 1.5R

    # กัน Order ซ้ำ — ถ้า signal_id นี้มีอยู่แล้วใน store ให้ข้ามไป
    if store.exists(signal_id):
        log.warning(f"  [order_confirmed] DUPLICATE signal_id={signal_id} — ข้าม")
        return jsonify({"status": "ignored", "msg": "duplicate signal_id"}), 200

    # ใหม่
    if side == "buy":
        entry = float(data.get("ask_entry", entry_high))  # Buy Entry บวก Spread แล้ว
        sl    = entry_low                                   # SL ไม่บวก Spread
    else:  # sell
        entry = entry_low                                   # Sell Entry ไม่บวก Spread
        sl    = float(data.get("ask_sl", entry_high))      # SL บวก Spread แล้ว

    # ส่งคำสั่งไป MT5
    mt5_ticket = place_pending_order(
        symbol=symbol,
        side=side,
        entry=entry,
        sl=sl,
        tp=tp,
        lot=lot,
        comment=f"1M2C_{signal_id}",  # comment ใน MT5 ใช้ trace กลับได้
    )

    if mt5_ticket is None:
        log.error(f"  [order_confirmed] MT5 ส่ง Order ไม่สำเร็จ signal_id={signal_id}")
        return jsonify({"status": "error", "msg": "mt5 order failed"}), 500

    # บันทึก State ลง Store
    store.add(
        signal_id=signal_id,
        symbol=symbol,
        side=side,
        entry=entry,
        sl=sl,
        tp=tp,
        lot=lot,
        mt5_ticket=mt5_ticket,
        state="pending",  # PENDING = ยังไม่ Fill
    )

    log.info(f"  [order_confirmed] MT5 ticket={mt5_ticket}  state=PENDING")
    return jsonify({"status": "ok", "ticket": mt5_ticket}), 200


def handle_order_filled(data: dict):
    """
    ราคาชน Entry → Order ถูก Fill แล้ว
    Flask แค่อัปเดต State เป็น active
    MT5 จัดการ SL/TP เองอยู่แล้ว ไม่ต้องทำอะไรเพิ่ม
    """
    signal_id = data["signal_id"]

    if not store.exists(signal_id):
        log.warning(f"  [order_filled] ไม่พบ signal_id={signal_id} ใน store")
        return jsonify({"status": "ignored", "msg": "signal_id not found"}), 200

    store.update_state(signal_id, "active")
    log.info(f"  [order_filled] signal_id={signal_id}  state → ACTIVE")
    return jsonify({"status": "ok"}), 200


def handle_cancel_pending(data: dict):
    """
    ราคาชน SL ก่อน Order Fill → Cancel Pending Order ใน MT5

    เงื่อนไข: Order ต้องยัง PENDING อยู่
    ถ้า ACTIVE แล้ว MT5 ปิดเอง Flask ไม่ต้องทำอะไร
    """
    signal_id = data["signal_id"]

    if not store.exists(signal_id):
        log.warning(f"  [cancel_pending] ไม่พบ signal_id={signal_id} ใน store")
        return jsonify({"status": "ignored", "msg": "signal_id not found"}), 200

    order = store.get(signal_id)

    # ตรวจ State — Cancel ได้เฉพาะ PENDING เท่านั้น
    if order["state"] != "pending":
        log.warning(
            f"  [cancel_pending] signal_id={signal_id} state={order['state']} "
            f"— ไม่ใช่ PENDING ข้าม"
        )
        return jsonify({"status": "ignored", "msg": "order not pending"}), 200

    log.info(
        f"  [cancel_pending] {order['side'].upper()} {order['symbol']}  "
        f"ticket={order['mt5_ticket']}  signal_id={signal_id}"
    )

    # ส่ง Cancel ไป MT5
    ok = cancel_pending_order(ticket=order["mt5_ticket"])

    if not ok:
        log.error(f"  [cancel_pending] MT5 Cancel ไม่สำเร็จ ticket={order['mt5_ticket']}")
        return jsonify({"status": "error", "msg": "mt5 cancel failed"}), 500

    store.update_state(signal_id, "cancelled")
    log.info(f"  [cancel_pending] signal_id={signal_id}  state → CANCELLED")
    return jsonify({"status": "ok"}), 200


def handle_breakeven(data: dict):
    """
    ราคาถึง 1R → เลื่อน SL มาที่ Entry (Breakeven)

    เงื่อนไข: Order ต้อง ACTIVE แล้วเท่านั้น
    ถ้ายัง PENDING → ยังไม่ Fill → ข้ามไป
    """
    signal_id = data["signal_id"]

    if not store.exists(signal_id):
        log.warning(f"  [breakeven] ไม่พบ signal_id={signal_id} ใน store")
        return jsonify({"status": "ignored", "msg": "signal_id not found"}), 200

    order = store.get(signal_id)

    # ตรวจ State — Breakeven ได้เฉพาะ ACTIVE เท่านั้น
    if order["state"] != "active":
        log.warning(
            f"  [breakeven] signal_id={signal_id} state={order['state']} "
            f"— ไม่ใช่ ACTIVE ข้าม"
        )
        return jsonify({"status": "ignored", "msg": "order not active"}), 200

    log.info(
        f"  [breakeven] {order['side'].upper()} {order['symbol']}  "
        f"ticket={order['mt5_ticket']}  เลื่อน SL → {order['entry']}"
    )

    # ส่งคำสั่งเลื่อน SL ไป MT5
    ok = move_sl_to_breakeven(
        ticket=order["mt5_ticket"],
        new_sl=order["entry"],  # SL ใหม่ = ราคา Entry เดิม
    )

    if not ok:
        log.error(f"  [breakeven] MT5 เลื่อน SL ไม่สำเร็จ ticket={order['mt5_ticket']}")
        return jsonify({"status": "error", "msg": "mt5 modify failed"}), 500

    store.update_state(signal_id, "breakeven")
    log.info(f"  [breakeven] signal_id={signal_id}  state → BREAKEVEN")
    return jsonify({"status": "ok"}), 200


# ════════════════════════════════════════════════════════════════════════════
# UTILITY ROUTES
# ════════════════════════════════════════════════════════════════════════════


@app.route("/orders", methods=["GET"])
def list_orders():
    """ดู State ของ Order ทั้งหมดที่ Flask รู้จัก (เพื่อ Debug)"""
    return jsonify(store.all()), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check สำหรับ ngrok ทดสอบว่า Server ทำงานอยู่"""
    return jsonify({"status": "ok", "time": datetime.now().isoformat()}), 200


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    log.info("Flask Webhook Server เริ่มทำงาน  port=5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
