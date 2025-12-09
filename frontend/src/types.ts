export type AudienceType = "B端" | "C端";

export interface AnalysisFormData {
  productName: string;
  persona: string;
  targetCustomer: string;
  audienceType: AudienceType;
  productKeywords: string;
  additionalContext?: string;
}

export interface MarketingCopy {
  channel: string;
  copy: string;
}

export interface PainPointCard {
  id: string;
  title: string;
  scenario: string;
  pain_point: string;
  solution: string;
  recommended_copies: MarketingCopy[];
  saved?: boolean;
}

export interface VoiceConfig {
  language: string;
  voice_style: string;
  age_group: string;
}

export interface Scene {
  id: number;
  title: string;
  visuals: string;
  voice_over: string;
  screen_text: string;
}

export interface VideoScript {
  headline: string;
  scenes: Scene[];
}

export interface AnalysisResponse {
  cards: PainPointCard[];
}

export interface ScriptResponse {
  script: VideoScript;
}

export interface VideoResponse {
  video_url: string;
  audio_url: string;
  job_id?: string;
  status?: string;
}

export interface VideoStatusResponse {
  job_id: string;
  status: string;
  video_url?: string;
  raw?: Record<string, unknown>;
}
