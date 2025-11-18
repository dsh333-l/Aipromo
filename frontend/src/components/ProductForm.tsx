import { ChangeEvent } from "react";
import { AnalysisFormData } from "../types";

interface ProductFormProps {
  value: AnalysisFormData;
  onChange: (data: AnalysisFormData) => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
}

export function ProductForm({ value, onChange, onAnalyze, isAnalyzing }: ProductFormProps) {
  const updateField = (key: keyof AnalysisFormData) => (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    onChange({ ...value, [key]: event.target.value });
  };

  return (
    <div className="panel left-panel">
      <div className="stepper">
        <span className="step-pill active">Step 1 · 产品输入</span>
        <span className="step-pill">Step 2 · AI 分析</span>
        <span className="step-pill">Step 3 · 视频生成</span>
      </div>
      <h2 className="section-title">基础信息</h2>
      <label>产品名称</label>
      <input placeholder="零食食品生产" value={value.productName} onChange={updateField("productName")} />

      <label>你的身份</label>
      <input placeholder="工厂老板 / 代理商 / 运营" value={value.persona} onChange={updateField("persona")} />

      <label>你想吸引谁</label>
      <input placeholder="零食供应链商" value={value.targetCustomer} onChange={updateField("targetCustomer")} />

      <label>受众人群</label>
      <select value={value.audienceType} onChange={updateField("audienceType")}>
        <option value="B端">B 端</option>
        <option value="C端">C 端</option>
      </select>

      <label>产品关键词</label>
      <textarea
        placeholder="零食供应链、办公零食、零食厂家..."
        value={value.productKeywords}
        onChange={updateField("productKeywords")}
      />

      <label>补充信息（可选）</label>
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
