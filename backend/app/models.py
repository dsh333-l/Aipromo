from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class AudienceType(str, Enum):
    b_end = "B端"
    c_end = "C端"


class ProductAnalysisRequest(BaseModel):
    product_name: str = Field(..., description="产品名称")
    persona: str = Field(..., description="用户身份角色，例如：工厂老板 / 代理商 / 运营")
    target_customer: str = Field(..., description="想要触达的目标客户，如：零食供应链商")
    audience_type: AudienceType = Field(..., description="受众人群类型：B端 或 C端")
    product_keywords: List[str] = Field(
        default_factory=list,
        description="与产品相关的多个关键词"
    )
    additional_context: Optional[str] = Field(
        default=None,
        description="补充信息，可选"
    )


class MarketingCopy(BaseModel):
    channel: str = Field(..., description="推荐投放渠道")
    copy: str = Field(..., description="具体的营销文案")

    class Config:
        protected_namespaces = ()


class PainPointCard(BaseModel):
    id: str
    title: str
    scenario: str
    pain_point: str
    solution: str
    recommended_copies: List[MarketingCopy]
    saved: bool = False


class ProductAnalysisResponse(BaseModel):
    cards: List[PainPointCard]


class VoiceConfig(BaseModel):
    language: str
    voice_style: str
    age_group: str


class GenerateScriptRequest(BaseModel):
    selected_card: PainPointCard
    voice: VoiceConfig
    video_style: str


class Scene(BaseModel):
    id: int
    title: str
    visuals: str
    voice_over: str
    screen_text: str


class VideoScript(BaseModel):
    headline: str
    scenes: List[Scene]


class GenerateScriptResponse(BaseModel):
    script: VideoScript


class GenerateVideoRequest(BaseModel):
    script: VideoScript
    voice: VoiceConfig
    video_style: str


class GenerateVideoResponse(BaseModel):
    video_url: str
    audio_url: str
