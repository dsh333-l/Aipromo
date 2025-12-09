import {
  AnalysisFormData,
  AnalysisResponse,
  PainPointCard,
  ScriptResponse,
  VideoResponse,
  VoiceConfig,
  VideoScript,
  VideoStatusResponse
} from "./types";

const API_BASE = "";

const jsonHeaders = {
  "Content-Type": "application/json"
};

function buildKeywords(raw: string): string[] {
  return raw
    .split(/\n|,|，/g)
    .map((item) => item.trim())
    .filter(Boolean);
}

export async function analyzeProduct(form: AnalysisFormData): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({
      product_name: form.productName,
      persona: form.persona,
      target_customer: form.targetCustomer,
      audience_type: form.audienceType,
      product_keywords: buildKeywords(form.productKeywords),
      additional_context: form.additionalContext
    })
  });

  if (!response.ok) {
    throw new Error(`分析失败：${response.statusText}`);
  }

  return response.json();
}

export async function generateScript(
  selectedCard: PainPointCard,
  voice: VoiceConfig,
  videoStyle: string
): Promise<ScriptResponse> {
  const response = await fetch(`${API_BASE}/api/generate_script`, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({
      selected_card: selectedCard,
      voice,
      video_style: videoStyle
    })
  });

  if (!response.ok) {
    throw new Error(`脚本生成失败：${response.statusText}`);
  }

  return response.json();
}

export async function generateVideo(
  script: VideoScript,
  voice: VoiceConfig,
  videoStyle: string
): Promise<VideoResponse> {
  const response = await fetch(`${API_BASE}/api/generate_video`, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({
      script,
      voice,
      video_style: videoStyle
    })
  });

  if (!response.ok) {
    throw new Error(`视频生成失败：${response.statusText}`);
  }

  return response.json();
}

export async function getVideoStatus(videoId: string): Promise<VideoStatusResponse> {
  const response = await fetch(`${API_BASE}/api/video_status?video_id=${encodeURIComponent(videoId)}`, {
    method: "GET",
    headers: jsonHeaders
  });
  if (!response.ok) {
    throw new Error(`查询视频状态失败：${response.statusText}`);
  }
  return response.json();
}
