import { VoiceConfig, VideoScript } from "../types";

interface VideoConfigProps {
  voice: VoiceConfig;
  videoStyle: string;
  onVoiceChange: (voice: VoiceConfig) => void;
  onVideoStyleChange: (style: string) => void;
  onGenerateScript: () => void;
  onGenerateVideo: () => void;
  script?: VideoScript;
  generatingScript: boolean;
  generatingVideo: boolean;
  videoUrl?: string;
  audioUrl?: string;
  disabled?: boolean;
}

export function VideoConfig({
  voice,
  videoStyle,
  onVoiceChange,
  onVideoStyleChange,
  onGenerateScript,
  onGenerateVideo,
  script,
  generatingScript,
  generatingVideo,
  videoUrl,
  audioUrl,
  disabled
}: VideoConfigProps) {
  const updateVoice = (key: keyof VoiceConfig) => (event: React.ChangeEvent<HTMLSelectElement>) =>
    onVoiceChange({ ...voice, [key]: event.target.value });

  return (
    <div className="panel right-panel">
      <div className="stepper">
        <span className="step-pill">Step 1 · 产品输入</span>
        <span className="step-pill">Step 2 · AI 分析</span>
        <span className="step-pill active">Step 3 · 视频生成</span>
      </div>

      <h2 className="section-title">配音 & 视频风格设置</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
        <div>
          <label>配音语言</label>
          <select value={voice.language} onChange={updateVoice("language")} disabled={disabled}>
            <option value="中文普通话">中文普通话</option>
            <option value="粤语">粤语</option>
            <option value="英语">英语</option>
          </select>
        </div>
        <div>
          <label>声线</label>
          <select value={voice.voice_style} onChange={updateVoice("voice_style")} disabled={disabled}>
            <option value="女声">女声</option>
            <option value="男声">男声</option>
            <option value="青年">青年</option>
            <option value="中年">中年</option>
          </select>
        </div>
        <div>
          <label>年龄段</label>
          <select value={voice.age_group} onChange={updateVoice("age_group")} disabled={disabled}>
            <option value="青年">青年</option>
            <option value="中年">中年</option>
            <option value="成熟">成熟</option>
          </select>
        </div>
        <div>
          <label>视频风格</label>
          <select value={videoStyle} onChange={(event) => onVideoStyleChange(event.target.value)} disabled={disabled}>
            <option value="工厂实力展示">工厂实力展示</option>
            <option value="商务路演风">商务路演风</option>
            <option value="短视频种草风">短视频种草风</option>
          </select>
        </div>
      </div>

      <div className="cta-footer" style={{ justifyContent: "flex-start", gap: 12 }}>
        <button className="secondary" onClick={onGenerateScript} disabled={generatingScript || disabled}>
          {generatingScript ? "生成脚本中..." : "生成分镜脚本"}
        </button>
        <button className="primary" onClick={onGenerateVideo} disabled={generatingVideo || !script || disabled}>
          {generatingVideo ? "视频生成中..." : "生成预览视频"}
        </button>
      </div>

      {script && (
        <div style={{ marginTop: 24, background: "#0f172a", color: "#e2e8f0", borderRadius: 16, padding: 20 }}>
          <h3 style={{ marginTop: 0, marginBottom: 12 }}>{script.headline}</h3>
          <ol style={{ margin: 0, paddingLeft: 18 }}>
            {script.scenes.map((scene) => (
              <li key={scene.id} style={{ marginBottom: 16 }}>
                <strong>{scene.title}</strong>
                <div style={{ fontSize: 14, lineHeight: 1.6 }}>
                  <p style={{ margin: "4px 0" }}>
                    <strong>画面：</strong>
                    {scene.visuals}
                  </p>
                  <p style={{ margin: "4px 0" }}>
                    <strong>旁白：</strong>
                    {scene.voice_over}
                  </p>
                  <p style={{ margin: "4px 0" }}>
                    <strong>屏幕文字：</strong>
                    {scene.screen_text}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}

      {(videoUrl || audioUrl) && (
        <div style={{ marginTop: 24, background: "#ecfccb", color: "#166534", borderRadius: 12, padding: 16 }}>
          <p style={{ margin: 0, fontWeight: 600 }}>生成完成 🎬</p>
          <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
            {videoUrl && (
              <a className="chip badge-success" href={videoUrl} target="_blank" rel="noreferrer">
                下载视频
              </a>
            )}
            {audioUrl && (
              <a className="chip" href={audioUrl} target="_blank" rel="noreferrer">
                下载配音
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default VideoConfig;
