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

BRAND_DECLARATION = ""


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

SCRIPT_PROMPT = """
你是资深短视频编导 + 资深广告文案（擅长 60-90 秒口播转化）。
请根据“已选卡片信息”和“视频/配音设定”，生成 3 条长文案的中文口播文案。
你的输出必须是严格可解析的 JSON（不要代码块，不要多余说明）。

【已选卡片信息】
- 标题：{title}
- 场景：{scenario}
- 痛点：{pain_point}
- 解决方案：{solution}

【视频设定】
- 视频风格：{video_style}
- 配音设定：{voice_language} · {voice_style} · {age_group}

【受众假设】
- 受众是谁：{audience}（如果未提供，默认“对该场景有明确需求的人”）
- 他们最在意：省钱 / 省时间 / 更简单 / 更稳定 / 更体面（从 pain_point 推断优先级）

【统一硬性要求】
1) 每条口播时长约 60-90 秒（约 240-360 个中文字符为主，可略浮动）。
2) 开头前 1-2 句必须是强钩子：反常识/戳痛点/提问/数字/对比/真实小尴尬，任选其一。
3) 全程像聊天：短句、多口语连接词（比如“说真的/你有没有/其实/我之前也/关键是”）。
4) 不要出现“Scene/镜头/画面/旁白提示”等制作提示词；不要出现“大家好我是XX”这种过度模板。
5) 不能夸张承诺（例如“100%有效”“立刻治好”“永久解决”）；避免绝对化用语。
6) 结尾必须有轻量 CTA：引导“评论关键词/私信/点链接/收藏/试一次”，但不要硬广腔。

【3条文案差异化规则（必须严格执行）】
- 文案1：痛点共鸣型（把痛点说透，说到“我就是这样”）
- 文案2：对比反差型（用“传统做法 vs 这个方案”的对比）
- 文案3：故事真实型（一个小故事：我/朋友/客户，前后变化）

【每条文案推荐结构（写作时遵循，但不要显式写出结构词）】
钩子 → 具体场景 → 痛点加深（1-2个细节）→ 解决方案亮相 → 关键好处（3点以内）→ 轻量 CTA

【质量自检（生成前在脑内检查，不要输出检查过程）】
- 是否够口语？读起来像人在说吗？
- 是否具体？有没有“细节画面感”（场景里的小动作/小尴尬/小代价）？
- 5条是否明显不同？是否没有重复句式和同一个开头套路？
- 是否只输出 JSON？是否无多余文本？

请输出 JSON：
{{ "headline": "文案标题",
  "copies": 
[ "口播文案1", 
  "口播文案2", 
  "口播文案3" ] 
}}

"""


XHS_PROMPT = """已选卡片信息：
- 标题：{title}
- 场景：{scenario}
- 痛点：{pain_point}
- 解决方案：{solution}

请生成适合小红书发布的文案，输出 JSON：
{{
  "copies": [
    "文案1",
    "文案2",
    "文案3",
    "文案4",
    "文案5"
  ]
}}

要求：必须输出 5 条，每条 80-160 字，带 3-5 个话题标签（#），语气真实、口语化，避免夸大。"""


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
    headline = data.get("headline") or "视频口播文案"

    # 优先支持单段口播文案
    full_voice = data.get("voice_over") or data.get("voiceOver")
    if isinstance(full_voice, str) and full_voice.strip():
        cleaned = full_voice.replace("Scene", "").replace("镜头", "").strip("：: ").strip()
        return VideoScript(
            headline=headline,
            scenes=[
                Scene(
                    id=1,
                    title="口播文案",
                    visuals="口播视频",
                    voice_over=cleaned,
                    screen_text=textwrap.shorten(headline, 32),
                )
            ],
        )

    copies_raw = data.get("copies")
    if isinstance(copies_raw, list) and copies_raw:
        scenes: List[Scene] = []
        for idx, item in enumerate(copies_raw, start=1):
            text = str(item).strip()
            if not text:
                continue
            cleaned = text.replace("Scene", "").replace("镜头", "").strip("：: ").strip()
            scenes.append(
                Scene(
                    id=idx,
                    title=f"文案 {idx}",
                    visuals="口播视频",
                    voice_over=cleaned,
                    screen_text=textwrap.shorten(headline, 32),
                )
            )
        if scenes:
            return VideoScript(headline=headline, scenes=scenes[:3])

    scenes_raw = data.get("scenes")
    if not isinstance(scenes_raw, list):
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
    hooks = [
        f"如果你还在为「{card.pain_point}」头疼，先听我说一句。",
        f"做门窗的朋友注意了，{card.pain_point}其实有更稳的解法。",
        f"不少渠道伙伴都在问：{card.pain_point}到底怎么解决？",
    ]
    bodies = [
        f"{card.scenario} 是我们经常听到的真实反馈。"
        f"很多项目一开始就栽在细节和流程上，表面看是工期问题，实则是标准与协同没对齐。"
        f"我们用「{card.solution}」把关键环节跑通，让交付更稳、沟通更快。"
        f"从选材到装配，再到现场交付的节点，都能做到“有依据、有节奏、有复盘”。",
        f"传统做法往往是每个环节都在补救，越补越乱。"
        f"我们把方案核心拆成三点：稳定交付、标准一致、响应更快，落地抓手就是「{card.solution}」。"
        f"这样一来，项目进度更可控，返工风险明显降低，客户体验也更稳定。",
        f"我举个真实小故事：之前有个工程客户就卡在{card.pain_point}上，"
        f"预算、时间、人力都被消耗。我们帮他重新梳理流程，用「{card.solution}」做了改造，"
        f"结果交付周期缩短、沟通成本下降，后续项目就轻松很多。",
    ]
    tail = "想知道具体怎么落地？留言或私信聊一聊。"

    scenes: List[Scene] = []
    for idx in range(3):
        voice_over = _wrap_brand_tag(f"{hooks[idx]} {bodies[idx]} {tail}")
        scenes.append(
            Scene(
                id=idx + 1,
                title=f"文案 {idx + 1}",
                visuals=req.video_style,
                voice_over=voice_over,
                screen_text=textwrap.shorten(card.solution, width=36, placeholder="..."),
            )
        )

    headline = f"{card.title} - 口播文案"
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
            audience="对该场景有明确需求的人",
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
                fallback_scenes = _fallback_script(req).scenes
                scenes = script.scenes
                if len(scenes) < 5:
                    scenes = scenes + fallback_scenes[len(scenes):5]
                wrapped = [
                    Scene(
                        id=s.id,
                        title=s.title,
                        visuals=s.visuals,
                        voice_over=_wrap_brand_tag(s.voice_over),
                        screen_text=s.screen_text,
                    )
                    for s in scenes
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

    def normalize_copies(raw: List[str]) -> List[str]:
        cleaned = [_wrap_brand_tag(str(item)) for item in raw if str(item).strip()]
        while len(cleaned) < 5:
            cleaned.append(
                _wrap_brand_tag(
                    f"{req.selected_card.title}：{req.selected_card.solution}已在多个项目验证，"
                    f"欢迎交流适配场景。#门窗 #系统窗 #工程渠道"
                )
            )
        return cleaned[:5]

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
                normalized = normalize_copies(copies)
                return GenerateXhsResponse(copies=normalized)
        except Exception:
            pass

    fallback = normalize_copies([
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
    ])
    return GenerateXhsResponse(copies=fallback)
