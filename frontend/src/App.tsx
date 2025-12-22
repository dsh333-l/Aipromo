import { useMemo, useState, useEffect } from "react";
import AnalysisPanel from "./components/AnalysisPanel";
import ProductForm from "./components/ProductForm";
import VideoConfig from "./components/VideoConfig";
import XhsPanel from "./components/XhsPanel";
import { analyzeProduct, generateScript, generateVideo, getVideoStatus, generateXhs } from "./api";
import {
  AnalysisFormData,
  PainPointCard,
  VoiceConfig,
  VideoScript
} from "./types";
import { WINDOW_MODELS } from "./data/windows/models";

const defaultForm: AnalysisFormData = {
  productName: WINDOW_MODELS[0]?.name || "门窗产品",
  persona: "门窗厂老板",
  targetCustomer: "门窗渠道商 / 工程客户",
  audienceType: "B端",
  productKeywords: WINDOW_MODELS[0]?.keywords.join("\n") || "铝合金门窗",
  provider: "openai",
  publishPlatform: "short_video",
};

const defaultVoice: VoiceConfig = {
  language: "中文普通话",
  voice_style: "女声",
  age_group: "青年"
};

type Step = 1 | 2 | 3;

function App() {
  const [formData, setFormData] = useState<AnalysisFormData>(defaultForm);
  const [cards, setCards] = useState<PainPointCard[]>([]);
  const [selectedCard, setSelectedCard] = useState<PainPointCard | null>(null);
  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [selectedWindowId, setSelectedWindowId] = useState<string>(WINDOW_MODELS[0]?.id || "");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isScriptLoading, setIsScriptLoading] = useState(false);
  const [isVideoLoading, setIsVideoLoading] = useState(false);

  const [voiceConfig, setVoiceConfig] = useState<VoiceConfig>(defaultVoice);
  const [videoStyle, setVideoStyle] = useState("工厂实力展示");

  const [script, setScript] = useState<VideoScript | undefined>();
  const [videoUrl, setVideoUrl] = useState<string | undefined>();
  const [audioUrl, setAudioUrl] = useState<string | undefined>();
  const [jobId, setJobId] = useState<string | undefined>();
  const [videoStatus, setVideoStatus] = useState<string | undefined>();
  const [isPolling, setIsPolling] = useState(false);
  const [xhsCopies, setXhsCopies] = useState<string[]>([]);
  const [selectedXhsIndex, setSelectedXhsIndex] = useState<number | null>(null);
  const [isXhsLoading, setIsXhsLoading] = useState(false);
  const buildWindowContext = (model: (typeof WINDOW_MODELS)[number]) => {
    const specLines = [
      `窗型：${model.windowType}`,
      `铝材：${model.aluminum}`,
      `喷涂：${model.coating}`,
      `开启方式：${model.opening}`,
      `玻璃：${model.glass}`,
      `五金：${model.hardware}`,
      `执手：${model.handle}`,
      `纱窗：${model.screen}`,
      `密封：${model.seal}`,
      `排水：${model.drainage}`,
      `水密/气密/抗风压：${model.waterTightness}/${model.airTightness}/${model.pressureResistance}`,
      `隔音/保温：${model.soundInsulation}/${model.insulation}`,
      `可视面：${model.visibleWidth}`,
      `颜色：木{${model.colorWood}} 铝{${model.colorAluminum}}`,
      `玻璃护栏：${model.glassRailing}`,
      `护角：${model.cornerGuard}`,
      `水性漆：${model.paint}`,
    ];
    return specLines.join("\n");
  };

  useEffect(() => {
    if (jobId && (!videoUrl || videoUrl.includes("video_status"))) {
      pollVideoStatus(jobId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  useEffect(() => {
    const model = WINDOW_MODELS.find((item) => item.id === selectedWindowId);
    if (model) {
      setFormData((prev) => ({
        ...prev,
        productName: model.name,
        productKeywords: model.keywords.join("\n"),
        additionalContext: buildWindowContext(model),
      }));
    }
  }, [selectedWindowId]);

  const [errorMessage, setErrorMessage] = useState<string | undefined>();

  const canProceedToVideo = useMemo(() => !!selectedCard, [selectedCard]);
  const isXhs = formData.publishPlatform === "xhs";

  const handleAnalyze = async () => {
    let formForRequest = formData;
    if (selectedWindowId) {
      const model = WINDOW_MODELS.find((item) => item.id === selectedWindowId);
      if (model) {
        formForRequest = {
          ...formData,
          productName: model.name,
          productKeywords: model.keywords.join("\n"),
          additionalContext: buildWindowContext(model),
        };
        setFormData(formForRequest);
      }
    }
    try {
      setIsAnalyzing(true);
      setErrorMessage(undefined);
      setCurrentStep(1);
      setSelectedCard(null);
      setScript(undefined);
      setVideoUrl(undefined);
      setAudioUrl(undefined);
      setJobId(undefined);
      setVideoStatus(undefined);
      setXhsCopies([]);
      setSelectedXhsIndex(null);

      const response = await analyzeProduct(formForRequest);
      setCards(response.cards);
      setCurrentStep(2);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorMessage(message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const selectCard = (card: PainPointCard) => {
    setSelectedCard(card);
    setScript(undefined);
    setVideoUrl(undefined);
    setAudioUrl(undefined);
    setJobId(undefined);
    setVideoStatus(undefined);
    setXhsCopies([]);
    setSelectedXhsIndex(null);
  };

  const toggleSave = (cardId: string) => {
    setCards((prev) =>
      prev.map((card) => (card.id === cardId ? { ...card, saved: !card.saved } : card))
    );
  };

  const ensureScript = async () => {
    if (!selectedCard) {
      setErrorMessage("请先采纳一条文案。");
      return;
    }
    try {
      setIsScriptLoading(true);
      setErrorMessage(undefined);
      const response = await generateScript(selectedCard, voiceConfig, videoStyle, formData.provider);
      setScript(response.script);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorMessage(message);
    } finally {
      setIsScriptLoading(false);
    }
  };

  const generateXhsCopies = async () => {
    if (!selectedCard) {
      setErrorMessage("请先采纳一条文案。");
      return;
    }
    try {
      setIsXhsLoading(true);
      setErrorMessage(undefined);
      const response = await generateXhs(selectedCard, formData.provider);
      setXhsCopies(response.copies);
      setSelectedXhsIndex(0);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorMessage(message);
    } finally {
      setIsXhsLoading(false);
    }
  };

  const generateVideoAssets = async () => {
    if (!script) {
      await ensureScript();
    }
    if (!selectedCard || !script) {
      return;
    }
    try {
      setIsVideoLoading(true);
      setErrorMessage(undefined);
      const response = await generateVideo(script, voiceConfig, videoStyle);
      setVideoUrl(response.video_url);
      setAudioUrl(response.audio_url);
      setJobId(response.job_id);
      setVideoStatus(response.status);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorMessage(message);
    } finally {
      setIsVideoLoading(false);
    }
  };

  const pollVideoStatus = (currentJobId: string, attempt = 0) => {
    const maxAttempts = 12;
    setIsPolling(true);
    getVideoStatus(currentJobId)
      .then((res) => {
        setVideoStatus(res.status);
        if (res.video_url) {
          setVideoUrl(res.video_url);
          setIsPolling(false);
          return;
        }
        if (attempt < maxAttempts) {
          setTimeout(() => pollVideoStatus(currentJobId, attempt + 1), 4000);
        } else {
          setIsPolling(false);
        }
      })
      .catch((err) => {
        setVideoStatus(err instanceof Error ? err.message : String(err));
        setIsPolling(false);
      });
  };

  const jumpToVideoStep = () => {
    if (!canProceedToVideo) {
      setErrorMessage("请选择一张要生成视频的卡片。");
      return;
    }
    setCurrentStep(3);
  };

  return (
    <div className="app-shell">
      <ProductForm
        value={formData}
        onChange={setFormData}
        onAnalyze={handleAnalyze}
        isAnalyzing={isAnalyzing}
        windowModels={WINDOW_MODELS}
        selectedWindowId={selectedWindowId}
        onSelectWindow={setSelectedWindowId}
      />

      {currentStep === 3 ? (
        isXhs ? (
          <XhsPanel
            copies={xhsCopies}
            generating={isXhsLoading}
            onGenerate={generateXhsCopies}
            selectedIndex={selectedXhsIndex}
            onSelect={(index) => setSelectedXhsIndex(index)}
          />
        ) : (
          <VideoConfig
            voice={voiceConfig}
            videoStyle={videoStyle}
            onVoiceChange={setVoiceConfig}
            onVideoStyleChange={setVideoStyle}
            onGenerateScript={ensureScript}
            onGenerateVideo={generateVideoAssets}
            script={script}
            generatingScript={isScriptLoading}
            generatingVideo={isVideoLoading}
            videoUrl={videoUrl}
            audioUrl={audioUrl}
            jobId={jobId}
            videoStatus={videoStatus}
            onPollStatus={() => jobId && pollVideoStatus(jobId)}
            isPolling={isPolling}
          />
        )
      ) : (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 16 }}>
          <AnalysisPanel
            cards={cards}
            selectedCardId={selectedCard?.id}
            onSelect={selectCard}
            onToggleSave={toggleSave}
            isLoading={isAnalyzing}
            publishPlatform={formData.publishPlatform}
          />
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button className="primary" onClick={jumpToVideoStep} disabled={!canProceedToVideo}>
              {isXhs ? "下一步：生成小红书文案" : "下一步：选择配音"}
            </button>
          </div>
        </div>
      )}

      {errorMessage && (
        <div
          style={{
            position: "fixed",
            right: 24,
            bottom: 24,
            background: "#fee2e2",
            color: "#b91c1c",
            padding: "16px 24px",
            borderRadius: 12,
            boxShadow: "0 8px 24px rgba(248, 113, 113, 0.25)"
          }}
        >
          {errorMessage}
        </div>
      )}
    </div>
  );
}

export default App;
