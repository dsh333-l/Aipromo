from __future__ import annotations

import json
import random
import textwrap
import uuid
from typing import List, Sequence

from ..models import (
    GenerateScriptRequest,
    GenerateXhsRequest,
    GenerateXhsResponse,
    MarketingCopy,
    PainPointCard,
    ProductAnalysisRequest,
    ProductAnalysisResponse,
    Scene,
    VideoScript,
)
from .llm import extract_json_block, llm_client


SYSTEM_PROMPT = """你是一名资深 ToB 品牌策略师，擅长拆解工厂、供应链、渠道的真实痛点，并生成结构化营销方案。需要保证输出内容可直接落在营销系统中。"""

BRAND_DECLARATION = "瑞明门窗，稳定交付，安全可信，共创增长"


def _wrap_brand_tag(text: str) -> str:
    if BRAND_DECLARATION in text:
        return text
    return f"{BRAND_DECLARATION}\n{text}\n{BRAND_DECLARATION}"

ANALYSIS_PROMPT = """输入信息：
- 产品名称：{product_name}
- 用户身份：{persona}
- 目标客户：{target_customer}
- 受众人群：{audience_type}
- 关键词：{keywords}

请输出 JSON，格式如下：
{{
  "cards": [
    {{
      "id": "可生成 uuid 或留空",
      "title": "痛点概括标题",
      "scenario": "业务场景及痛点",
      "pain_point": "对方真实痛点描述",
      "solution": "我方解决方案",
      "recommended_copies": [
        {{"channel": "客户私聊/朋友圈/公众号/短视频等", "copy": "具体营销文案"}}
      ]
    }}
  ]
}}

请返回 3~4 条卡片，语言口语化且聚焦生意场景。"""

SCRIPT_PROMPT = """已选卡片信息：
- 标题：{title}
- 场景：{scenario}
- 痛点：{pain_point}
- 解决方案：{solution}

视频风格：{video_style}
配音设定：{voice_language} · {voice_style} · {age_group}

请输出 JSON：
{{
  "headline": "脚本标题",
  "scenes": [
    {{
      "title": "Scene 1",
      "visuals": "画面描述 + 调度",
      "voice_over": "口播文案，符合配音语言，完整自然，不要出现“Scene”/镜头编号等提示词",
      "screen_text": "屏幕文字或字幕"
    }}
  ]
}}

要求：
- 只生成口播自然表达，不要在 voice_over 里出现 “Scene”/“镜头” 等提示词。
- 画面描述配合视频风格，但旁白保持连贯口语。
- 3~5 个分镜即可。"""

XHS_PROMPT = """已选卡片信息：
- 标题：{title}
- 场景：{scenario}
- 痛点：{pain_point}
- 解决方案：{solution}

请生成适合小红书发布的文案，输出 JSON：
{{
  "copies": [
    "文案1",
    "文案2"
  ]
}}

要求：每条 80-160 字，带 3-5 个话题标签（#），语气真实、口语化，避免夸大。"""


PAIN_POINT_PATTERNS = [
    (
        "供应链效率瓶颈导致订单流失",
        "关键客户在补货高峰期频繁缺货，导致终端门店体验直线下降。",
        "我们提供可视化库存预警与柔性排产能力，帮助客户保持 48 小时内常规补货。",
    ),
    (
        "品牌差异化不足难以破圈",
        "同类零食品牌扎堆，渠道方缺乏差异化故事支撑。",
        "提供联合定制与包装设计团队，强化渠道私域故事打造。",
    ),
    (
        "食品安全与溯源码缺失背锅风险高",
        "合作方担心代工厂的品控与追溯体系，导致合作推进缓慢。",
        "我们具备全链条质检与区块链追溯编码，合作即接入监管后台。",
    ),
    (
        "动销内容缺乏导致复购疲软",
        "渠道手上缺少高频新品、场景化素材，促销拉新难度高。",
        "提供月度产品力报告+素材模板，让客户一键更新活动素材。",
    ),
]

CHANNEL_TEMPLATES = {
    "客户私聊": "【{title}】我们近期升级了 {solution}，能否安排 15 分钟了解一下？",
    "朋友圈": "做零食供应链的朋友看过来：{pain_point}。我们用 {solution}，近期开放合作窗口。",
    "公众号": "聚焦 {title}，拆解真实案例：{scenario}，我们用 {solution} 解题，详情见文末联系。",
    "短视频脚本": "画面切入工厂现场，旁白：{scenario}。下一镜转到解决方案，强调 {solution}。",
}

VIDEO_STYLE_HINTS = {
    "工厂实力展示": [
        "展示生产线高速运转，强调产能与品控。",
        "穿插质检实验室画面，突出严选原料与追溯体系。",
        "以合作客户合影收尾，强化供应链稳定感。",
    ],
    "商务路演风": [
        "开场搭建市场机会，用数据图示 B 端需求爆发。",
        "主体拆解痛点与解决方案，用图表+案例交替呈现。",
        "结尾抛出合作 CTA，引导预约深聊。",
    ],
    "短视频种草风": [
        "开场以场景口播抛出痛点，引发共鸣。",
        "中段快速展示产品亮点镜头+字幕，节奏紧凑。",
        "尾部加抢购或预约口播，强化行动号召。",
    ],
}


def _build_marketing_copies(title: str, scenario: str, pain_point: str, solution: str) -> List[MarketingCopy]:
    copies: List[MarketingCopy] = []
    for channel, template in CHANNEL_TEMPLATES.items():
        text = template.format(
            title=title,
            scenario=scenario,
            pain_point=pain_point,
            solution=solution,
        )
        copies.append(MarketingCopy(channel=channel, ad_copy=_wrap_brand_tag(text)))
    return copies


def _parse_llm_cards(raw_cards: Sequence[dict]) -> List[PainPointCard]:
    cards: List[PainPointCard] = []
    for entry in raw_cards:
        title = entry.get("title")
        solution = entry.get("solution")
        pain_point = entry.get("pain_point")
        scenario = entry.get("scenario")
        if not (title and solution and pain_point and scenario):
            continue

        copies_raw = entry.get("recommended_copies", [])
        if not isinstance(copies_raw, list):
            copies_raw = []

        copies: List[MarketingCopy] = []
        for copy in copies_raw:
            channel = copy.get("channel") or "客户私聊"
            copy_text = copy.get("copy") or copy.get("content")
            if not copy_text:
                continue
            copies.append(MarketingCopy(channel=channel, ad_copy=copy_text))

        if not copies:
            copies = _build_marketing_copies(title, scenario, pain_point, solution)

        cards.append(
            PainPointCard(
                id=entry.get("id") or str(uuid.uuid4()),
                title=title,
                scenario=scenario,
                pain_point=pain_point,
                solution=solution,
                recommended_copies=[
                    MarketingCopy(channel=c.channel, ad_copy=_wrap_brand_tag(c.ad_copy)) for c in copies
                ],
            )
        )
    return cards


def _fallback_cards(req: ProductAnalysisRequest) -> List[PainPointCard]:
    keywords = ", ".join(req.product_keywords) if req.product_keywords else req.product_name
    persona_fragment = f"{req.persona}在做{req.product_name}"
    random.shuffle(PAIN_POINT_PATTERNS)

    cards: List[PainPointCard] = []
    for idx, (title, pain, solution) in enumerate(PAIN_POINT_PATTERNS[:3], start=1):
        scenario = textwrap.shorten(
            f"{persona_fragment} 时常会遇到 {pain} "
            f"目标客群（{req.target_customer}）对此格外敏感，尤其是关注 {keywords} 相关指标。",
            width=140,
            placeholder="...",
        )
        cards.append(
            PainPointCard(
                id=str(uuid.uuid4()),
                title=title,
                scenario=scenario,
                pain_point=pain,
                solution=solution,
                recommended_copies=_build_marketing_copies(title, scenario, pain, solution),
            )
        )
    return cards


def analyze_product(req: ProductAnalysisRequest) -> ProductAnalysisResponse:
    if llm_client.is_configured():
        prompt = ANALYSIS_PROMPT.format(
            product_name=req.product_name,
            persona=req.persona,
            target_customer=req.target_customer,
            audience_type=req.audience_type,
            keywords=", ".join(req.product_keywords) if req.product_keywords else "用户未提供",
        )
        try:
            response = llm_client.chat(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.85,
                provider=req.provider,
            )
            parsed = json.loads(extract_json_block(response.content))
            cards_data = parsed.get("cards", [])
            if isinstance(cards_data, list):
                cards = _parse_llm_cards(cards_data)
                if cards:
                    return ProductAnalysisResponse(cards=cards)
        except Exception:
            pass

    return ProductAnalysisResponse(cards=_fallback_cards(req))


def _parse_llm_script(data: dict) -> VideoScript | None:
    headline = data.get("headline")
    scenes_raw = data.get("scenes")
    if not (headline and isinstance(scenes_raw, list)):
        return None

    scenes: List[Scene] = []
    for idx, scene in enumerate(scenes_raw, start=1):
        visuals = scene.get("visuals")
        voice_over = scene.get("voice_over") or scene.get("voiceOver")
        if isinstance(voice_over, str):
            voice_over = voice_over.replace("Scene", "").replace("镜头", "").strip("：: ").strip()
        screen_text = scene.get("screen_text") or scene.get("screenText")
        title = scene.get("title") or f"Scene {idx}"
        if not (visuals and voice_over):
            continue
        scenes.append(
            Scene(
                id=idx,
                title=title,
                visuals=visuals,
                voice_over=voice_over,
                screen_text=screen_text or textwrap.shorten(visuals, 32),
            )
        )

    if not scenes:
        return None

    return VideoScript(headline=headline, scenes=scenes)


def _fallback_script(req: GenerateScriptRequest) -> VideoScript:
    card = req.selected_card
    style_hints = VIDEO_STYLE_HINTS.get(req.video_style, VIDEO_STYLE_HINTS["商务路演风"])
    scenes: List[Scene] = []
    for idx, hint in enumerate(style_hints, start=1):
        voice_over = {
            1: f"最近不少 {card.title} 项目的渠道伙伴都提到：{card.pain_point}",
            2: f"我们用方案「{card.solution}」做到了：{card.scenario}",
            3: f"想了解你所在场景如何落地，欢迎和我们聊聊，支持打样/联合共创。",
        }.get(idx, f"{card.solution}，满足 {card.scenario}")

        scenes.append(
            Scene(
                id=idx,
                title=f"Scene {idx}",
                visuals=hint,
                voice_over=voice_over,
                screen_text=textwrap.shorten(card.solution, width=36, placeholder="..."),
            )
        )

    headline = f"{card.title} - {req.video_style}"
    return VideoScript(headline=headline, scenes=scenes)


def generate_video_script(req: GenerateScriptRequest) -> VideoScript:
    if llm_client.is_configured():
        prompt = SCRIPT_PROMPT.format(
            title=req.selected_card.title,
            scenario=req.selected_card.scenario,
            pain_point=req.selected_card.pain_point,
            solution=req.selected_card.solution,
            video_style=req.video_style,
            voice_language=req.voice.language,
            voice_style=req.voice.voice_style,
            age_group=req.voice.age_group,
        )
        try:
            response = llm_client.chat(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                provider=req.provider,
            )
            parsed = json.loads(extract_json_block(response.content))
            script = _parse_llm_script(parsed)
            if script:
                wrapped = [
                    Scene(
                        id=s.id,
                        title=s.title,
                        visuals=s.visuals,
                        voice_over=s.voice_over,
                        screen_text=s.screen_text,
                    )
                    for s in script.scenes
                ]
                return VideoScript(headline=script.headline, scenes=wrapped)
        except Exception:
            pass

    return _fallback_script(req)


def generate_xhs_copies(req: GenerateXhsRequest) -> GenerateXhsResponse:
    prompt = XHS_PROMPT.format(
        title=req.selected_card.title,
        scenario=req.selected_card.scenario,
        pain_point=req.selected_card.pain_point,
        solution=req.selected_card.solution,
    )

    if llm_client.is_configured():
        try:
            response = llm_client.chat(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                provider=req.provider,
            )
            parsed = json.loads(extract_json_block(response.content))
            copies = parsed.get("copies", [])
            if isinstance(copies, list) and copies:
                normalized = [_wrap_brand_tag(str(item)) for item in copies if str(item).strip()]
                if normalized:
                    return GenerateXhsResponse(copies=normalized)
        except Exception:
            pass

    fallback = [
        _wrap_brand_tag(
            f"{req.selected_card.title}：不少合作方都在意{req.selected_card.pain_point}，"
            f"我们用{req.selected_card.solution}解决关键卡点。#门窗 #工程渠道 #品质交付"
        ),
        _wrap_brand_tag(
            f"{req.selected_card.scenario}正是很多渠道商的真实场景。"
            f"配置{req.selected_card.solution}后，交付更稳、反馈更快。#门窗厂家 #系统窗 #靠谱供应"
        ),
        _wrap_brand_tag(
            f"如果你也在寻找更稳定的门窗合作伙伴，{req.selected_card.title}这件事我们已经跑通。"
            f"欢迎交流对标。#门窗品牌 #工程项目 #合作共赢"
        ),
    ]
    return GenerateXhsResponse(copies=fallback)
