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
      <div className="panel-intro">
        <p className="subtitle">生成后可选择一条作为最终发布文案，支持直接复制发布。</p>
        <div className="meta">
          <span className="chip">口语化表达</span>
          <span className="chip">3-5 个话题标签</span>
          <span className="chip">品牌宣言收尾</span>
        </div>
      </div>

      <div className="cta-footer" style={{ justifyContent: "flex-start" }}>
        <button className="primary" onClick={onGenerate} disabled={generating}>
          {generating ? "文案生成中..." : "生成小红书文案"}
        </button>
      </div>

      {copies.length > 0 ? (
        <div className="xhs-grid" style={{ marginTop: 16 }}>
          {copies.slice(0, 5).map((copy, index) => (
            <div
              key={`${index}-${copy.slice(0, 10)}`}
              className={`xhs-card ${selectedIndex === index ? "selected" : ""}`}
              onClick={() => onSelect(index)}
            >
              <div className="title">
                <strong>文案 {index + 1}</strong>
                {selectedIndex === index && <span className="chip">已选择</span>}
              </div>
              <p style={{ margin: 0, whiteSpace: "pre-line", lineHeight: 1.6 }}>{copy}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="xhs-empty">
          <p style={{ margin: 0, fontWeight: 600 }}>暂无文案</p>
          <p style={{ margin: "6px 0 0", fontSize: 13 }}>点击“生成小红书文案”获取可发布的内容。</p>
        </div>
      )}
    </div>
  );
}

export default XhsPanel;
