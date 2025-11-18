import { PainPointCard } from "../types";

interface AnalysisPanelProps {
  cards: PainPointCard[];
  selectedCardId?: string;
  onSelect: (card: PainPointCard) => void;
  onToggleSave: (cardId: string) => void;
  isLoading: boolean;
}

export function AnalysisPanel({ cards, selectedCardId, onSelect, onToggleSave, isLoading }: AnalysisPanelProps) {
  return (
    <div className="panel right-panel">
      <div className="stepper">
        <span className="step-pill">Step 1 · 产品输入</span>
        <span className="step-pill active">Step 2 · AI 分析</span>
        <span className="step-pill">Step 3 · 视频生成</span>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 className="section-title" style={{ marginBottom: 0 }}>
          AI 痛点 & 卖点卡片
        </h2>
        {isLoading && <span className="chip">智能分析中...</span>}
      </div>

      {!cards.length && (
        <div style={{ marginTop: 40, textAlign: "center", color: "#64748b" }}>
          {isLoading ? "正在智能分析产品，请稍候..." : "提交产品信息，AI 将生成多条营销洞察。"}
        </div>
      )}

      <div className="cards-grid">
        {cards.map((card) => {
          const isSelected = card.id === selectedCardId;
          return (
            <div
              key={card.id}
              style={{
                borderRadius: 18,
                border: isSelected ? "2px solid #6366f1" : "1px solid #e2e8f0",
                background: "linear-gradient(135deg, rgba(15,23,42,0.86), rgba(30,64,175,0.8))",
                color: "#fff",
                padding: 20,
                display: "flex",
                flexDirection: "column",
                gap: 12,
                minHeight: 280,
                boxShadow: isSelected ? "0 18px 40px rgba(99,102,241,0.35)" : "0 12px 24px rgba(15,23,42,0.25)"
              }}
            >
              <span className="chip badge-success" style={{ alignSelf: "flex-start" }}>
                卖点洞察
              </span>
              <h3 style={{ margin: "0 0 12px 0", fontSize: 20 }}>{card.title}</h3>
              <p style={{ margin: 0, fontSize: 14, lineHeight: 1.6, color: "rgba(241,245,249,0.9)" }}>{card.scenario}</p>
              <p style={{ margin: 0, fontSize: 14 }}>
                <strong>核心痛点：</strong>
                {card.pain_point}
              </p>
              <p style={{ margin: 0, fontSize: 14 }}>
                <strong>解决方案：</strong>
                {card.solution}
              </p>
              <div style={{ marginTop: "auto" }}>
                <p style={{ fontSize: 13, opacity: 0.8, marginBottom: 6 }}>推荐营销文案：</p>
                <ul style={{ margin: 0, paddingLeft: 18, color: "rgba(226,232,240,0.92)", fontSize: 13, lineHeight: 1.6 }}>
                  {card.recommended_copies.map((copy) => (
                    <li key={copy.channel}>
                      <strong>{copy.channel}：</strong>
                      {copy.copy}
                    </li>
                  ))}
                </ul>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 12 }}>
                <button className="secondary" onClick={() => onToggleSave(card.id)} style={{ flex: 1, marginRight: 8 }}>
                  {card.saved ? "已保存" : "保存文案"}
                </button>
                <button className="primary" onClick={() => onSelect(card)} style={{ flex: 1 }}>
                  {isSelected ? "已采纳" : "采纳"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AnalysisPanel;
