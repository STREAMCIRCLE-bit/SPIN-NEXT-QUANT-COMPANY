---
name: trading-journal
description: >
  Skill สำหรับสร้างและจัดการระบบบันทึกการเทรด (Trading Journal) ที่เชื่อมกับ Google Sheets
  ครอบคลุมทั้งการบันทึก Trade Log, วิเคราะห์ Performance อัตโนมัติ, บันทึกจิตวิทยาการเทรด
  และสร้าง Investor Report สำหรับนำเสนอนักลงทุน
  Trigger เมื่อ: บันทึกเทรด, trade journal, trade log, จดบันทึกการเทรด,
  วิเคราะห์ผลเทรด, สรุปผลเทรด, psychology journal, อารมณ์การเทรด,
  investor report, รายงานนักลงทุน, สร้าง journal, trading diary,
  Google Sheets trading, "จดเทรด", "บันทึกออเดอร์", "สรุปพอร์ต",
  "รายงานผลงาน", "journal จิตวิทยา", "สร้างเว็บบันทึกเทรด",
  "trade tracker", "performance report", "equity curve",
  หรือคำขอใดก็ตามที่เกี่ยวกับการเก็บข้อมูลการเทรดและวิเคราะห์ผล
  ใช้ Skill นี้แม้ผู้ใช้ไม่ได้พูดตรงๆ ว่า "journal" แต่บริบทบ่งบอกว่าต้องการ
  บันทึก ติดตาม หรือวิเคราะห์ประวัติการเทรดของตัวเอง
---

# Trading Journal — AI Agent Skill

Skill สำหรับสร้างระบบบันทึกการเทรดแบบครบวงจร ใช้ **Google Sheets** เป็น Database
ออกแบบมาเพื่อ CEO ขององค์กร Quant Trading Research ใช้งานเองและนำเสนอ HNW Investors

---

## Architecture Overview

```
Google Sheets (Database)
    ├── Sheet: TradeLog       — ทุก Trade ที่เปิด/ปิด
    ├── Sheet: Psychology     — บันทึกอารมณ์ + บทเรียน
    ├── Sheet: DailyStats     — สรุปรายวัน (auto-calculate)
    └── Sheet: Config         — ตั้งค่า Account, Risk Rules
         │
         │  Google Apps Script (Web App API)
         ▼
React Web App (Frontend)
    ├── 📝 Trade Entry Form   — บันทึก Trade
    ├── 📊 Dashboard          — Performance Metrics
    ├── 🧠 Psychology Tab     — Journal อารมณ์
    └── 📈 Investor View      — รายงานสำหรับ HNW
```

---

## Module 1: Google Sheets Schema

เมื่อสร้าง Google Sheets ให้ใช้ Schema นี้เป็น Blueprint

### Sheet: TradeLog

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | trade_id | TEXT | Auto-generate: TRD-YYYYMMDD-XXX |
| B | strategy_name | TEXT | ชื่อ Strategy ที่ใช้ |
| C | instrument | TEXT | เช่น EURUSD, XAUUSD, BTCUSD |
| D | direction | TEXT | BUY / SELL |
| E | entry_date | DATETIME | วันเวลาเปิด |
| F | entry_price | NUMBER | ราคาเข้า |
| G | sl_price | NUMBER | Stop Loss |
| H | tp_price | NUMBER | Take Profit |
| I | lot_size | NUMBER | ขนาด Lot |
| J | exit_date | DATETIME | วันเวลาปิด |
| K | exit_price | NUMBER | ราคาออก |
| L | pnl_usd | NUMBER | กำไร/ขาดทุน (USD) |
| M | pnl_pct | NUMBER | กำไร/ขาดทุน (%) |
| N | rr_actual | NUMBER | Risk:Reward ที่ได้จริง |
| O | result | TEXT | WIN / LOSS / BE (Break-even) |
| P | duration_hours | NUMBER | ระยะเวลาถือ (ชม.) |
| Q | screenshot_url | URL | ลิงก์ภาพหน้าจอ (Google Drive) |
| R | notes | TEXT | หมายเหตุ |
| S | session | TEXT | Asian / London / NY |
| T | day_of_week | TEXT | Mon-Fri (auto from entry_date) |

**Auto-calculated columns (สูตร Google Sheets):**
- `pnl_pct` = `pnl_usd / account_balance * 100`
- `rr_actual` = ถ้า WIN: `(exit_price - entry_price) / (entry_price - sl_price)`, ถ้า SELL กลับสูตร
- `result` = ถ้า `pnl_usd > 0` → WIN, ถ้า `< 0` → LOSS, ถ้า `= 0` → BE
- `duration_hours` = `(exit_date - entry_date) * 24`
- `day_of_week` = `TEXT(entry_date, "ddd")`

### Sheet: Psychology

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | date | DATE | วันที่ |
| B | trade_id | TEXT | เชื่อมกับ TradeLog (optional) |
| C | emotion_before | TEXT | อารมณ์ก่อนเทรด: Calm / Anxious / Greedy / FOMO / Revenge / Confident |
| D | emotion_after | TEXT | อารมณ์หลังเทรด: Satisfied / Frustrated / Regret / Neutral / Relief |
| E | followed_plan | BOOLEAN | ทำตามแผนหรือไม่ TRUE/FALSE |
| F | mistake_type | TEXT | None / Early Entry / Late Exit / Oversize / No SL / Revenge Trade / FOMO |
| G | lesson | TEXT | บทเรียนที่ได้ |
| H | confidence_score | NUMBER | 1-10 ความมั่นใจในวันนั้น |
| I | market_condition | TEXT | Trending / Ranging / Volatile / Calm |
| J | sleep_hours | NUMBER | ชั่วโมงนอน (ปัจจัยที่ส่งผลต่อการตัดสินใจ) |

### Sheet: DailyStats

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | date | DATE | วันที่ |
| B | total_trades | NUMBER | จำนวนเทรดวันนั้น |
| C | wins | NUMBER | จำนวน WIN |
| D | losses | NUMBER | จำนวน LOSS |
| E | daily_pnl_usd | NUMBER | กำไร/ขาดทุนรวมวันนั้น |
| F | daily_pnl_pct | NUMBER | % ต่อทุน |
| G | cumulative_pnl | NUMBER | กำไรสะสม |
| H | equity | NUMBER | มูลค่าพอร์ตปัจจุบัน |
| I | daily_winrate | NUMBER | Winrate วันนั้น (%) |
| J | max_drawdown | NUMBER | Max DD ณ วันนั้น (%) |
| K | plan_adherence | NUMBER | % ที่ทำตามแผน (from Psychology) |

### Sheet: Config

| Key | Value | Description |
|-----|-------|-------------|
| account_name | SPIN-NEXT-QUANT | ชื่อบัญชี |
| initial_balance | 100000 | ทุนเริ่มต้น (USD) |
| current_balance | (auto) | ทุนปัจจุบัน |
| max_risk_per_trade | 2 | % เสี่ยงต่อเทรด |
| max_daily_loss | 5 | % ขาดทุนสูงสุดต่อวัน |
| max_drawdown_limit | 20 | % DD สูงสุดที่ยอมรับ |
| broker | (broker name) | ชื่อโบรกเกอร์ |
| account_type | Live / Demo | ประเภทบัญชี |

---

## Module 2: Google Apps Script (API)

เมื่อสร้าง Web App ให้สร้าง Google Apps Script ที่ทำหน้าที่เป็น API

Apps Script ต้องมี endpoints เหล่านี้:

### Endpoint List

| Action | Method | Description |
|--------|--------|-------------|
| addTrade | POST | เพิ่ม Trade ใหม่ |
| updateTrade | POST | อัปเดต Trade (ปิดออเดอร์) |
| getTrades | GET | ดึง Trade ทั้งหมด (filter by date range) |
| addPsychology | POST | เพิ่มบันทึกจิตวิทยา |
| getPsychology | GET | ดึงบันทึกจิตวิทยา |
| getDailyStats | GET | ดึงสรุปรายวัน |
| getPerformance | GET | ดึง Performance Metrics รวม |
| getConfig | GET | ดึงตั้งค่า |

### Performance Metrics ที่ต้องคำนวณ (getPerformance)

```
Metrics ที่ต้อง return:
- total_trades      : จำนวนเทรดทั้งหมด
- win_rate          : Winrate รวม (%)
- profit_factor     : Gross Profit / Gross Loss
- avg_rr            : Average Risk:Reward ที่ได้จริง
- best_trade        : กำไรมากสุด (USD)
- worst_trade       : ขาดทุนมากสุด (USD)
- max_drawdown_pct  : Max Drawdown (%)
- sharpe_ratio      : Sharpe Ratio (ใช้ daily returns)
- sortino_ratio     : Sortino Ratio
- expectancy        : (Winrate × Avg Win) - (Lossrate × Avg Loss)
- avg_duration_hrs  : ระยะเวลาถือเฉลี่ย
- total_pnl_usd     : กำไร/ขาดทุนรวม
- total_pnl_pct     : % ต่อทุนเริ่มต้น
- equity_curve      : Array ของ cumulative equity [date, value]
- monthly_returns   : Array ของ monthly return [month, pct]
- win_streak        : ชนะติดต่อกันมากสุด
- loss_streak       : แพ้ติดต่อกันมากสุด
- best_day          : วันที่กำไรมากสุด
- worst_day         : วันที่ขาดทุนมากสุด
```

### Sharpe Ratio Calculation

```javascript
// คำนวณใน Apps Script
function calcSharpeRatio(dailyReturns) {
  var avg = dailyReturns.reduce((a,b) => a+b, 0) / dailyReturns.length;
  var variance = dailyReturns.reduce((sum, r) => sum + Math.pow(r - avg, 2), 0) / dailyReturns.length;
  var stdDev = Math.sqrt(variance);
  if (stdDev === 0) return 0;
  var annualizedReturn = avg * 252;
  var annualizedStdDev = stdDev * Math.sqrt(252);
  return annualizedReturn / annualizedStdDev;
}
```

---

## Module 3: React Web App Structure

เมื่อสร้าง Frontend ให้ใช้โครงสร้างนี้:

### Pages / Tabs

1. **Dashboard** (หน้าแรก)
   - Equity Curve chart (Recharts Line)
   - KPI Cards: Winrate, Sharpe, Max DD, Total P&L, Profit Factor
   - Monthly Returns heatmap
   - Recent Trades table (5 รายการล่าสุด)

2. **Trade Log** (บันทึกเทรด)
   - Form: เพิ่ม Trade ใหม่
   - Table: แสดง Trade ทั้งหมด (sortable, filterable)
   - Quick Stats: สรุปด้านบน

3. **Psychology** (จิตวิทยา)
   - Form: บันทึกอารมณ์ + บทเรียน
   - Charts: Emotion distribution, Plan adherence trend
   - Mistake frequency analysis

4. **Investor Report** (สำหรับ HNW)
   - Clean, professional layout (ไม่มี Psychology data)
   - Key Metrics: Sharpe, Max DD, Monthly Returns, Equity Curve
   - Strategy allocation breakdown
   - Risk management summary
   - Export as PDF button (optional Phase 2)

### Design Tokens (Dark Theme — สอดคล้องกับ Org Chart)

```
Background   : #0a0a1a
Card BG      : #111827
Border       : #1e293b
Text Primary : #f1f5f9
Text Muted   : rgba(255,255,255,0.5)
Accent Red   : #e94560  (loss / danger)
Accent Green : #22c55e  (profit / success)
Accent Blue  : #00d2ff  (info / charts)
Accent Purple: #a855f7  (psychology)
Accent Amber : #f59e0b  (warning)
Font Code    : 'JetBrains Mono', monospace
Font Body    : 'Noto Sans Thai', sans-serif
```

---

## Module 4: Investor Report View

รายงานสำหรับ HNW Investors ต้องแสดงข้อมูลเหล่านี้:

### Header
- ชื่อองค์กร: SPIN-NEXT QUANT
- Period: ช่วงเวลาที่แสดง
- Report Date: วันที่ออกรายงาน

### Performance Summary
- Net Return (%)
- Sharpe Ratio
- Max Drawdown (%)
- Profit Factor
- Win Rate (%)
- Total Trades

### Charts ที่ต้องมี
- Equity Curve (cumulative)
- Monthly Returns Bar Chart
- Drawdown Chart (underwater)
- Win/Loss Distribution

### Risk Metrics
- VaR (95%) — estimated from daily returns
- Expected Shortfall (CVaR)
- Longest Drawdown Duration
- Recovery Factor

### ข้อควรระวัง
- ห้ามแสดง Psychology data ใน Investor View
- ห้ามแสดง Trade-level detail (แสดงเฉพาะ aggregate)
- ต้องมี Disclaimer: "Past performance is not indicative of future results"
- แสดงเฉพาะข้อมูล Live Account (ไม่รวม Demo)

---

## Module 5: MT5 Integration (Phase 2)

สำหรับ Phase 2 — ดึง Trade จาก MT5 อัตโนมัติ:

```python
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def export_trades_to_sheet(days_back=30):
    """ดึง Trade History จาก MT5 แล้วส่งเข้า Google Sheets"""
    mt5.initialize()
    
    from_date = datetime.now() - timedelta(days=days_back)
    to_date = datetime.now()
    
    deals = mt5.history_deals_get(from_date, to_date)
    
    if deals is None or len(deals) == 0:
        print("No deals found")
        return
    
    df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
    
    # Filter เฉพาะ Trade จริง (ไม่รวม deposit/withdrawal)
    df = df[df['type'].isin([0, 1])]  # 0=buy, 1=sell
    
    # Map to Journal Schema
    journal_data = []
    for _, row in df.iterrows():
        journal_data.append({
            'instrument': row['symbol'],
            'direction': 'BUY' if row['type'] == 0 else 'SELL',
            'entry_date': datetime.fromtimestamp(row['time']).isoformat(),
            'entry_price': row['price'],
            'lot_size': row['volume'],
            'pnl_usd': row['profit'],
            'commission': row['commission'],
            'swap': row['swap'],
        })
    
    # TODO: Send to Google Sheets via Apps Script API
    return journal_data
```

---

## Coding Rules (สอดคล้องกับองค์กร)

- Google Apps Script: ใช้ `doGet()` / `doPost()` deploy เป็น Web App
- React: ใช้ Tailwind utility classes, Recharts สำหรับ charts
- CORS: Apps Script Web App ต้อง deploy แบบ "Anyone" เพื่อให้ Frontend เรียกได้
- Auth: Phase 1 ไม่มี Auth (ใช้คนเดียว), Phase 2 เพิ่ม API key ง่ายๆ
- Error Handling: ทุก API call ต้องมี try/catch และแสดง error message ชัดเจน
- ข้อมูลเงิน: แสดงทศนิยม 2 ตำแหน่ง, ใช้ comma separator
- ข้อมูล %: แสดงทศนิยม 2 ตำแหน่ง

---

## Output Checklist

เมื่อสร้าง Trading Journal ต้องส่งมอบ:

1. **Google Sheets Template** — พร้อม Schema + สูตร + ข้อมูลตัวอย่าง
2. **Google Apps Script Code** — API ที่ deploy ได้ทันที
3. **React Web App** — Frontend ที่ใช้งานได้ทันที
4. **Setup Guide** — คู่มือติดตั้ง step-by-step
5. **Sample Data** — ข้อมูล Trade ตัวอย่าง 10-20 รายการ

---

## Reference Files

อ่านไฟล์เหล่านี้เมื่อต้องการรายละเอียดเพิ่ม:
- `references/google-apps-script-template.md` — โค้ด Apps Script เต็ม
- `references/sample-data.md` — ข้อมูลตัวอย่างสำหรับทดสอบ
