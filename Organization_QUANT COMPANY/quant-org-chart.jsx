import { useState } from "react";

const orgData = {
  id: "ceo",
  title: "CEO",
  name: "Chief Executive Officer",
  dept: "executive",
  desc: "กำหนดทิศทางองค์กร ตัดสินใจ Deploy Strategy จัดสรรทุน",
  children: [
    {
      id: "cqs",
      title: "CQS",
      name: "Chief Quantitative Strategist",
      dept: "executive",
      desc: "กำหนดกรอบวิจัย เกณฑ์ผ่าน/ไม่ผ่าน ตัดสินว่า Strategy ใดเข้า Forward Test",
      children: [
        {
          id: "research",
          title: "Research & Strategy",
          name: "แผนกวิจัยและพัฒนากลยุทธ์",
          dept: "research",
          desc: "สร้างสมมติฐาน พัฒนา Trading Model Backtest",
          children: [
            { id: "qr", title: "Quant Researcher", name: "นักวิจัยเชิงปริมาณ", dept: "research", desc: "สร้างสมมติฐาน พัฒนา Alpha Model ทดสอบ Statistical Edge" },
            { id: "de", title: "Data Engineer", name: "วิศวกรข้อมูล", dept: "research", desc: "จัดการ Data Pipeline ทำความสะอาดข้อมูล Price/Volume/Sentiment" },
            { id: "be", title: "Backtest Engineer", name: "วิศวกร Backtesting", dept: "research", desc: "สร้าง Backtesting Infrastructure ป้องกัน Bias ทุกรูปแบบ" },
          ],
        },
        {
          id: "eval",
          title: "Evaluation & QA",
          name: "แผนกประเมินผลและตรวจสอบคุณภาพ",
          dept: "eval",
          desc: "วิเคราะห์ผลลัพธ์ตามเกณฑ์ ตรวจสอบ Code & Logic",
          children: [
            { id: "pa", title: "Performance Analyst", name: "นักวิเคราะห์ผลการดำเนินงาน", dept: "eval", desc: "วิเคราะห์ Winrate, Sharpe, Sortino, Max DD, Profit Factor แยกรายปี" },
            { id: "qa", title: "QA Engineer", name: "วิศวกรตรวจสอบคุณภาพ", dept: "eval", desc: "ตรวจสอบ Data Integrity, Code Logic, ป้องกัน Overfit หลุดเข้า Forward Test" },
          ],
        },
      ],
    },
    {
      id: "cro",
      title: "CRO",
      name: "Chief Risk Officer",
      dept: "executive",
      desc: "ดูแล Portfolio-level Risk, Correlation Limit, Position Sizing, Max Exposure",
      children: [
        {
          id: "portfolio",
          title: "Execution & Portfolio",
          name: "แผนกบริหารพอร์ตและดำเนินการเทรด",
          dept: "portfolio",
          desc: "จัดสรรน้ำหนักกลยุทธ์ ดูแล Bot Execution",
          children: [
            { id: "ps", title: "Portfolio Strategist", name: "นักกลยุทธ์พอร์ตโฟลิโอ", dept: "portfolio", desc: "ออกแบบ Portfolio Composition ลด Correlation กระจายความเสี่ยง" },
            { id: "ee", title: "Execution Engineer", name: "วิศวกรดำเนินการเทรด", dept: "portfolio", desc: "พัฒนา Trading Bot, Order Routing, Slippage Monitoring" },
            { id: "to", title: "Trading Operator", name: "เจ้าหน้าที่เฝ้าระบบเทรด", dept: "portfolio", desc: "เฝ้าระบบ Live ตรวจสอบว่า Bot ทำงานตรงตาม Signal" },
          ],
        },
      ],
    },
    {
      id: "cto",
      title: "CTO",
      name: "Chief Technology Officer",
      dept: "executive",
      desc: "ดูแลโครงสร้างพื้นฐานทั้งหมด Data Pipeline → Backtest → Execution",
      children: [
        {
          id: "infra",
          title: "Infrastructure & DevOps",
          name: "แผนกโครงสร้างพื้นฐานและ DevOps",
          dept: "infra",
          desc: "ดูแล Server, Deployment, Monitoring, Database",
          children: [
            { id: "devops", title: "DevOps / MLOps", name: "วิศวกร DevOps/MLOps", dept: "infra", desc: "ดูแล Server, CI/CD, Monitoring, Alerting System" },
            { id: "dbe", title: "Database Engineer", name: "วิศวกรฐานข้อมูล", dept: "infra", desc: "จัดการ Storage สำหรับ Historical Data, Trade Log, Performance Record" },
          ],
        },
      ],
    },
  ],
};

const deptColors = {
  executive: { bg: "#1a1a2e", border: "#e94560", text: "#e94560", glow: "rgba(233,69,96,0.3)" },
  research: { bg: "#0f1b2d", border: "#00d2ff", text: "#00d2ff", glow: "rgba(0,210,255,0.25)" },
  eval: { bg: "#1a0f2e", border: "#a855f7", text: "#a855f7", glow: "rgba(168,85,247,0.25)" },
  portfolio: { bg: "#0f2e1a", border: "#22c55e", text: "#22c55e", glow: "rgba(34,197,94,0.25)" },
  infra: { bg: "#2e1a0f", border: "#f59e0b", text: "#f59e0b", glow: "rgba(245,158,11,0.25)" },
};

const deptLabels = {
  executive: "ฝ่ายบริหาร",
  research: "แผนกวิจัย",
  eval: "แผนกประเมินผล",
  portfolio: "แผนกบริหารพอร์ต",
  infra: "แผนก Infra",
};

function OrgNode({ node, level = 0, selectedId, onSelect }) {
  const colors = deptColors[node.dept];
  const isSelected = selectedId === node.id;
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div
        onClick={() => onSelect(node.id === selectedId ? null : node.id)}
        style={{
          background: isSelected ? colors.border : colors.bg,
          border: `2px solid ${colors.border}`,
          borderRadius: level === 0 ? 16 : 10,
          padding: level <= 1 ? "14px 22px" : "10px 16px",
          cursor: "pointer",
          textAlign: "center",
          minWidth: level <= 1 ? 160 : 130,
          maxWidth: 200,
          boxShadow: isSelected ? `0 0 20px ${colors.glow}, 0 0 40px ${colors.glow}` : `0 2px 12px rgba(0,0,0,0.4)`,
          transition: "all 0.25s ease",
          position: "relative",
        }}
      >
        <div style={{
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          fontSize: level === 0 ? 18 : level === 1 ? 15 : 13,
          fontWeight: 700,
          color: isSelected ? "#0a0a1a" : colors.text,
          letterSpacing: 1,
        }}>
          {node.title}
        </div>
        <div style={{
          fontFamily: "'Noto Sans Thai', 'Sarabun', sans-serif",
          fontSize: 11,
          color: isSelected ? "#0a0a1a" : "rgba(255,255,255,0.6)",
          marginTop: 3,
          lineHeight: 1.3,
        }}>
          {node.name}
        </div>
      </div>

      {hasChildren && (
        <>
          <div style={{ width: 2, height: 20, background: `linear-gradient(to bottom, ${colors.border}, rgba(255,255,255,0.1))` }} />
          <div style={{ display: "flex", gap: level <= 1 ? 16 : 10, alignItems: "flex-start", position: "relative" }}>
            {node.children.length > 1 && (
              <div style={{
                position: "absolute",
                top: 0,
                left: "calc(50% - " + ((node.children.length - 1) * (level <= 1 ? 100 : 75)) + "px)",
                right: "calc(50% - " + ((node.children.length - 1) * (level <= 1 ? 100 : 75)) + "px)",
                height: 2,
                background: `linear-gradient(to right, transparent, ${colors.border}, transparent)`,
              }} />
            )}
            {node.children.map((child) => (
              <div key={child.id} style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <div style={{ width: 2, height: 20, background: colors.border, opacity: 0.5 }} />
                <OrgNode node={child} level={level + 1} selectedId={selectedId} onSelect={onSelect} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function findNode(node, id) {
  if (node.id === id) return node;
  if (node.children) {
    for (const child of node.children) {
      const found = findNode(child, id);
      if (found) return found;
    }
  }
  return null;
}

export default function QuantOrgChart() {
  const [selectedId, setSelectedId] = useState(null);
  const selectedNode = selectedId ? findNode(orgData, selectedId) : null;

  return (
    <div style={{
      background: "#0a0a1a",
      minHeight: "100vh",
      padding: "30px 16px",
      fontFamily: "'Noto Sans Thai', 'Sarabun', sans-serif",
      overflow: "auto",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+Thai:wght@300;400;600;700&display=swap" rel="stylesheet" />

      <div style={{ textAlign: "center", marginBottom: 30 }}>
        <h1 style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 22,
          fontWeight: 700,
          color: "#e94560",
          letterSpacing: 3,
          margin: 0,
        }}>
          QUANT TRADING RESEARCH ORG
        </h1>
        <p style={{ color: "rgba(255,255,255,0.4)", fontSize: 13, marginTop: 6, letterSpacing: 1 }}>
          AI-Powered Systematic Trading Organization
        </p>

        <div style={{ display: "flex", justifyContent: "center", gap: 16, marginTop: 16, flexWrap: "wrap" }}>
          {Object.entries(deptLabels).map(([key, label]) => (
            <div key={key} style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: 3, background: deptColors[key].border }} />
              <span style={{ color: "rgba(255,255,255,0.5)", fontSize: 11 }}>{label}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "center", overflowX: "auto", paddingBottom: 30 }}>
        <OrgNode node={orgData} selectedId={selectedId} onSelect={setSelectedId} />
      </div>

      {selectedNode && (
        <div style={{
          maxWidth: 600,
          margin: "0 auto",
          padding: 20,
          background: deptColors[selectedNode.dept].bg,
          border: `1px solid ${deptColors[selectedNode.dept].border}`,
          borderRadius: 12,
          boxShadow: `0 0 30px ${deptColors[selectedNode.dept].glow}`,
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <span style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 18,
              fontWeight: 700,
              color: deptColors[selectedNode.dept].text,
            }}>
              {selectedNode.title}
            </span>
            <span style={{
              fontSize: 11,
              color: deptColors[selectedNode.dept].text,
              opacity: 0.7,
              border: `1px solid ${deptColors[selectedNode.dept].border}`,
              padding: "2px 8px",
              borderRadius: 4,
            }}>
              {deptLabels[selectedNode.dept]}
            </span>
          </div>
          <div style={{ fontSize: 14, color: "rgba(255,255,255,0.8)", marginBottom: 6 }}>
            {selectedNode.name}
          </div>
          <div style={{ fontSize: 13, color: "rgba(255,255,255,0.55)", lineHeight: 1.6 }}>
            {selectedNode.desc}
          </div>
        </div>
      )}

      <div style={{
        textAlign: "center",
        marginTop: 24,
        color: "rgba(255,255,255,0.25)",
        fontSize: 11,
        letterSpacing: 1,
      }}>
        คลิกที่ตำแหน่งเพื่อดูรายละเอียด
      </div>
    </div>
  );
}
