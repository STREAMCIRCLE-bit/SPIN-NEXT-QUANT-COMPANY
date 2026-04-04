"""
order_store.py — เก็บ State ของ Order แต่ละ signal_id ใน memory

State transitions:
  pending   → active     (order_filled)
  active    → breakeven  (breakeven)
  pending   → cancelled  (cancel_pending)
  active    → closed     (MT5 ปิดเอง TP/SL — Flask รับรู้ผ่าน order_filled สุดท้าย)

หมายเหตุ: ใช้ dict ใน memory ธรรมดาก่อน
ถ้าต้องการ persist ข้ามการ restart ให้เปลี่ยนเป็น SQLite ในอนาคต
"""

from datetime import datetime
from typing import Optional


class OrderStore:
    def __init__(self):
        # key = signal_id (int), value = dict ข้อมูล Order
        self._store: dict[int, dict] = {}

    def add(
        self,
        signal_id: int,
        symbol: str,
        side: str,
        entry: float,
        sl: float,
        tp: float,
        lot: float,
        mt5_ticket: int,
        state: str = "pending",
    ) -> None:
        self._store[signal_id] = {
            "signal_id": signal_id,
            "symbol": symbol,
            "side": side,  # "buy" | "sell"
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "lot": lot,
            "mt5_ticket": mt5_ticket,
            "state": state,  # pending | active | breakeven | cancelled | closed
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    def exists(self, signal_id: int) -> bool:
        return signal_id in self._store

    def get(self, signal_id: int) -> Optional[dict]:
        return self._store.get(signal_id)

    def update_state(self, signal_id: int, new_state: str) -> None:
        if signal_id in self._store:
            self._store[signal_id]["state"] = new_state
            self._store[signal_id]["updated_at"] = datetime.now().isoformat()

    def all(self) -> dict:
        """คืน dict ทั้งหมด — ใช้กับ /orders endpoint เพื่อ Debug"""
        return self._store
