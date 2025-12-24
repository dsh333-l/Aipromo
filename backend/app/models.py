from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
try:  # pydantic v2
    from pydantic import ConfigDict  # type: ignore
except ImportError:  # pragma: no cover
    ConfigDict = None  # type: ignore


class AudienceType(str, Enum):
    b_end = "B端"
    c_end = "C端"


class ProductAnalysisRequest(BaseModel):
    product_name: str = Field(..., description="产品名称")
    persona: str = Field(..., description="用户身份角色，例如：工厂老板 / 代理商 / 运营")
    target_customer: str = Field(..., description="想要触达的目标客户，如：零食供应链商")
    audience_type: AudienceType = Field(..., description="受众人群类型：B端 或 C端")
    provider: Optional[str] = Field(default=None, description="llm 提供商，如 openai/deepseek/chatgpt")
    publish_platform: Optional[str] = Field(default=None, description="发布平台，如 short_video/xhs")
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
    ad_copy: str = Field("", alias="copy", description="具体的营销文案")

    if ConfigDict is not None:
        model_config = ConfigDict(populate_by_name=True, protected_namespaces=(), extra="ignore")
    else:  # pragma: no cover - pydantic v1 fallback
        class Config:
            protected_namespaces = ()
            allow_population_by_field_name = True
            extra = "ignore"


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
    provider: Optional[str] = Field(default=None, description="llm 提供商，如 openai/deepseek/chatgpt")


class GenerateXhsRequest(BaseModel):
    selected_card: PainPointCard
    provider: Optional[str] = Field(default=None, description="llm 提供商，如 openai/deepseek/chatgpt")


class GenerateXhsResponse(BaseModel):
    copies: List[str]


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
    avatar_id: Optional[str] = None


class GenerateVideoResponse(BaseModel):
    video_url: str
    audio_url: str
    job_id: Optional[str] = None
    status: Optional[str] = None


class HeygenStatusResponse(BaseModel):
    job_id: str
    status: str
    video_url: Optional[str] = None
    raw: Optional[dict] = None
