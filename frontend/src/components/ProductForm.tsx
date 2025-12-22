import { ChangeEvent } from "react";
import { AnalysisFormData } from "../types";
import { WindowModel } from "../data/windows/models";

interface ProductFormProps {
  value: AnalysisFormData;
  onChange: (data: AnalysisFormData) => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  windowModels: WindowModel[];
  selectedWindowId: string;
  onSelectWindow: (id: string) => void;
}

export function ProductForm({
  value,
  onChange,
  onAnalyze,
  isAnalyzing,
  windowModels,
  selectedWindowId,
  onSelectWindow,
}: ProductFormProps) {
  const updateField = (key: keyof AnalysisFormData) => (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    onChange({ ...value, [key]: event.target.value });
  };

  const selectedWindow = windowModels.find((item) => item.id === selectedWindowId);

  return (
    <div className="panel left-panel">
      <div className="brand-banner">
        <img src="/amberg.png" alt="AMBERG Logo" />
        <span className="tagline">主动健康门窗 · 品质严选</span>
      </div>
      <div className="stepper">
        <span className="step-pill active">Step 1 · 产品输入</span>
        <span className="step-pill">Step 2 · AI 分析</span>
        <span className="step-pill">
          Step 3 · {value.publishPlatform === "xhs" ? "小红书文案" : "视频生成"}
        </span>
      </div>
      <h2 className="section-title">门窗产品信息</h2>

      <label>门窗型号</label>
      <select value={selectedWindowId} onChange={(e) => onSelectWindow(e.target.value)}>
        {windowModels.map((model) => (
          <option key={model.id} value={model.id}>
            {model.name}
          </option>
        ))}
      </select>

      {selectedWindow && (
        <div style={{ marginBottom: 16, padding: 12, borderRadius: 12, background: "#f8fafc", border: "1px solid #e2e8f0" }}>
          <p style={{ margin: "4px 0", fontWeight: 700 }}>{selectedWindow.name}</p>
          <p style={{ margin: "4px 0", fontSize: 13, color: "#475569" }}>窗型：{selectedWindow.windowType}</p>
          <ul style={{ margin: "6px 0 0 16px", padding: 0, fontSize: 13, color: "#334155", lineHeight: 1.5 }}>
            <li>铝材：{selectedWindow.aluminum}</li>
            <li>喷涂：{selectedWindow.coating}</li>
            <li>开启方式：{selectedWindow.opening}</li>
            <li>玻璃：{selectedWindow.glass}</li>
            <li>五金：{selectedWindow.hardware}</li>
            <li>纱窗：{selectedWindow.screen}</li>
            <li>密封：{selectedWindow.seal}</li>
            <li>排水：{selectedWindow.drainage}</li>
            <li>气密/水密/抗风压：{selectedWindow.airTightness}/{selectedWindow.waterTightness}/{selectedWindow.pressureResistance}</li>
          </ul>
        </div>
      )}

      <label>产品名称</label>
      <input placeholder="门窗型号名称" value={value.productName} onChange={updateField("productName")} />

      <label>发布平台</label>
      <select value={value.publishPlatform ?? "short_video"} onChange={updateField("publishPlatform")}>
        <option value="short_video">短视频平台</option>
        <option value="xhs">小红书</option>
      </select>

      <label>模型提供商</label>
      <select value={value.provider ?? "openai"} onChange={updateField("provider")}>
        <option value="openai">ChatGPT (OpenAI 兼容)</option>
        <option value="deepseek">DeepSeek</option>
      </select>

      <label>你的身份</label>
      <input placeholder="门窗厂老板 / 经销商 / 设计师" value={value.persona} onChange={updateField("persona")} />

      <label>你想吸引谁</label>
      <input placeholder="门窗渠道商 / 工程客户 / 设计院" value={value.targetCustomer} onChange={updateField("targetCustomer")} />

      <input type="hidden" value={value.audienceType} readOnly />

      <label>产品关键词（自动带入，可编辑）</label>
      <textarea
        placeholder="铝合金、隐藏排水、德国五金..."
        value={value.productKeywords}
        onChange={updateField("productKeywords")}
      />

      <label>补充信息（可选，默认带入型号规格）</label>
      <textarea placeholder="渠道现状 / 竞争对手 / 诉求..." value={value.additionalContext ?? ""} onChange={updateField("additionalContext")} />

      <div className="cta-footer">
        <button className="primary" disabled={isAnalyzing} onClick={onAnalyze}>
          {isAnalyzing ? "分析中..." : "AI 分析"}
        </button>
      </div>
    </div>
  );
}

export default ProductForm;
