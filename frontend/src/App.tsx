import { useMemo, useState } from "react";
import AnalysisPanel from "./components/AnalysisPanel";
import ProductForm from "./components/ProductForm";
import VideoConfig from "./components/VideoConfig";
import { analyzeProduct, generateScript, generateVideo } from "./api";
import {
  AnalysisFormData,
  PainPointCard,
  VoiceConfig,
  VideoScript
} from "./types";

const defaultForm: AnalysisFormData = {
  productName: "零食食品生产",
  persona: "工厂老板",
  targetCustomer: "零食供应链商",
  audienceType: "B端",
  productKeywords: "零食供应链\nOEM 代工\n食品安全"
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

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isScriptLoading, setIsScriptLoading] = useState(false);
  const [isVideoLoading, setIsVideoLoading] = useState(false);

  const [voiceConfig, setVoiceConfig] = useState<VoiceConfig>(defaultVoice);
  const [videoStyle, setVideoStyle] = useState("工厂实力展示");

  const [script, setScript] = useState<VideoScript | undefined>();
  const [videoUrl, setVideoUrl] = useState<string | undefined>();
  const [audioUrl, setAudioUrl] = useState<string | undefined>();

  const [errorMessage, setErrorMessage] = useState<string | undefined>();

  const canProceedToVideo = useMemo(() => !!selectedCard, [selectedCard]);

  const handleAnalyze = async () => {
    try {
      setIsAnalyzing(true);
      setErrorMessage(undefined);
      setCurrentStep(1);
      setSelectedCard(null);
      setScript(undefined);
      setVideoUrl(undefined);
      setAudioUrl(undefined);

      const response = await analyzeProduct(formData);
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
      const response = await generateScript(selectedCard, voiceConfig, videoStyle);
      setScript(response.script);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorMessage(message);
    } finally {
      setIsScriptLoading(false);
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
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setErrorMessage(message);
    } finally {
      setIsVideoLoading(false);
    }
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
      <ProductForm value={formData} onChange={setFormData} onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />

      {currentStep === 3 ? (
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
        />
      ) : (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 16 }}>
          <AnalysisPanel
            cards={cards}
            selectedCardId={selectedCard?.id}
            onSelect={selectCard}
            onToggleSave={toggleSave}
            isLoading={isAnalyzing}
          />
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button className="primary" onClick={jumpToVideoStep} disabled={!canProceedToVideo}>
              下一步：选择配音
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
