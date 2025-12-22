interface XhsPanelProps {
  copies: string[];
  generating: boolean;
  onGenerate: () => void;
  selectedIndex: number | null;
  onSelect: (index: number) => void;
}

export function XhsPanel({ copies, generating, onGenerate, selectedIndex, onSelect }: XhsPanelProps) {
  return (
    <div className="panel right-panel">
      <div className="brand-banner" style={{ marginBottom: 10 }}>
        <img src="/amberg.png" alt="AMBERG Logo" />
        <span className="tagline">主动健康门窗 · 品质严选</span>
      </div>
      <div className="stepper">
        <span className="step-pill">Step 1 · 产品输入</span>
        <span className="step-pill">Step 2 · AI 分析</span>
        <span className="step-pill active">Step 3 · 小红书文案</span>
      </div>

      <h2 className="section-title">小红书发布文案</h2>
      <p style={{ marginTop: 0, color: "#475569", fontSize: 13 }}>
        生成后可选择一条作为最终发布文案。
      </p>

      <div className="cta-footer" style={{ justifyContent: "flex-start" }}>
        <button className="primary" onClick={onGenerate} disabled={generating}>
          {generating ? "文案生成中..." : "生成小红书文案"}
        </button>
      </div>

      {copies.length > 0 && (
        <div style={{ marginTop: 16, display: "grid", gap: 12 }}>
          {copies.map((copy, index) => (
            <div
              key={`${index}-${copy.slice(0, 10)}`}
              style={{
                borderRadius: 14,
                padding: 14,
                border: selectedIndex === index ? "2px solid #1e5bff" : "1px solid #e2e8f0",
                background: "#ffffff",
                boxShadow: "0 10px 24px rgba(15, 45, 120, 0.12)",
              }}
              onClick={() => onSelect(index)}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <strong>文案 {index + 1}</strong>
                {selectedIndex === index && <span className="chip">已选择</span>}
              </div>
              <p style={{ margin: 0, whiteSpace: "pre-line", lineHeight: 1.6 }}>{copy}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default XhsPanel;
