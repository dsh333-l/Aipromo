from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Tuple, Union

import requests

from ..models import GenerateVideoRequest, HeygenStatusResponse


ASSETS_DIR = Path(__file__).resolve().parent.parent / "generated"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
BRAND_DECLARATION = os.getenv("BRAND_DECLARATION", "瑞明门窗，稳定交付，安全可信，共创增长")


def _timestamp_slug() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S%f")


def _write_placeholder(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def _build_heygen_payload(req: GenerateVideoRequest) -> dict:
    script = req.script
    # 直接生成口播文案：去掉重复的品牌宣言，仅在全文末尾附加一次
    voice_lines = []
    for scene in script.scenes:
        cleaned = scene.voice_over.replace(BRAND_DECLARATION, "").strip()
        if cleaned:
            voice_lines.append(cleaned)

    full_text = "\n".join(voice_lines).strip()
    if BRAND_DECLARATION:
        full_text = f"{full_text}\n{BRAND_DECLARATION}"

    avatar_id = req.avatar_id or os.getenv("HEYGEN_AVATAR_ID", "Miyu_standing_office_front")
    avatar_style = os.getenv("HEYGEN_AVATAR_STYLE", "normal")
    voice_id = os.getenv("HEYGEN_VOICE_ID", "119caed25533477ba63822d5d1552d25")

    payload: dict = {
        "title": script.headline,
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": avatar_style,
                },
                "voice": {
                    "type": "text",
                    "input_text": full_text,
                    "voice_id": voice_id,
                },
            }
        ],
        "dimension": {"width": 1280, "height": 720},
    }

    if os.getenv("HEYGEN_BACKGROUND_MUSIC_ID"):
        payload["background"] = {"music_id": os.getenv("HEYGEN_BACKGROUND_MUSIC_ID")}

    if os.getenv("HEYGEN_BRAND_LOGO_URL"):
        payload["logo_url"] = os.getenv("HEYGEN_BRAND_LOGO_URL")

    if os.getenv("HEYGEN_CALLBACK_URL"):
        payload["callback_url"] = os.getenv("HEYGEN_CALLBACK_URL")

    return payload


def _call_heygen(req: GenerateVideoRequest, slug: str) -> tuple[str | None, str | None, str | None, Path | None]:
    """
    Send script to HeyGen API.
    Returns: (video_url or job url, job_id, error_message, debug_file)
    """
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        return None, None, "HEYGEN_API_KEY 未配置，未触发调用。", None

    # 默认使用官方示例的 v2 生成接口，可通过 HEYGEN_API_URL 覆盖
    endpoint = os.getenv("HEYGEN_API_URL", "https://api.heygen.com/v2/video/generate")
    headers = {
        "x-api-key": api_key,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = _build_heygen_payload(req)
    debug_file = ASSETS_DIR / f"heygen_debug_{slug}.json"

    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        debug_file.write_text(
            json.dumps(
                {
                    "error": str(exc),
                    "hint": "检查 HEYGEN_API_URL 与 payload 是否符合官方文档（示例: https://api.heygen.com/v2/video/generate）",
                    "endpoint": endpoint,
                    "payload": payload,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return None, None, str(exc), debug_file

    data_block = data.get("data") or {}
    video_url = data_block.get("video_url") or data_block.get("download_url")
    job_id = data_block.get("video_id") or data_block.get("id")

    debug_file.write_text(
        json.dumps({"response": data, "endpoint": endpoint, "payload": payload}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 如果没有视频链接但有 job_id，返回查询链接
    if not video_url and job_id:
        status_base = os.getenv("HEYGEN_STATUS_URL", "https://api.heygen.com/v1/video_status.get?video_id=")
        video_url = status_base.format(video_id=job_id) if "{video_id}" in status_base else f"{status_base}{job_id}"

    return video_url, job_id, None, debug_file


def generate_video_assets(req: GenerateVideoRequest) -> Tuple[Union[Path, str], Union[Path, str], str | None]:
    """
    - 优先调用 HeyGen API 生成视频，返回远端链接或查询链接。
    - 如果未配置 HeyGen 或调用失败，落到本地占位文件。
    """
    script = req.script
    slug = _timestamp_slug()

    # 尝试调用 HeyGen
    video_url, job_id, heygen_error, debug_file = _call_heygen(req, slug)

    summary_lines = [
        f"视频风格: {req.video_style}",
        f"配音: {req.voice.language} · {req.voice.voice_style} · {req.voice.age_group}",
        f"HeyGen 调用: {'成功' if video_url else '未触发/失败'}",
        f"HeyGen 错误: {heygen_error or '无'}",
        f"HeyGen 调试文件: {debug_file.name if debug_file else '无'}",
        f"job_id: {job_id or '无'}",
        f"video_url: {video_url or '无'}",
        "",
        "分镜脚本：",
    ]
    for scene in script.scenes:
        summary_lines.append(f"- {scene.title}: 画面={scene.visuals} | 旁白={scene.voice_over} | 字幕={scene.screen_text}")

    video_path = ASSETS_DIR / f"demo_video_{slug}.txt"
    audio_path = ASSETS_DIR / f"demo_voice_{slug}.txt"

    _write_placeholder(video_path, "\n".join(summary_lines))
    _write_placeholder(
        audio_path,
        "这是一个配音占位文件。后续可接入真实 TTS 输出。\n\n完整旁白：\n" + "\n".join(scene.voice_over for scene in script.scenes),
    )

    # 如果 HeyGen 返回了远端地址，则 video_url 为字符串；否则返回本地占位路径
    final_video = video_url or video_path
    final_audio = audio_path

    return final_video, final_audio, job_id


def check_heygen_status(video_id: str) -> HeygenStatusResponse:
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        return HeygenStatusResponse(job_id=video_id, status="unconfigured", video_url=None, raw={"error": "HEYGEN_API_KEY missing"})

    status_base = os.getenv("HEYGEN_STATUS_URL", "https://api.heygen.com/v1/video_status.get?video_id=")
    url = status_base.format(video_id=video_id) if "{video_id}" in status_base else f"{status_base}{video_id}"
    headers = {"x-api-key": api_key, "accept": "application/json"}

    try:
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return HeygenStatusResponse(job_id=video_id, status="error", video_url=None, raw={"error": str(exc), "url": url})

    data_block = data.get("data") or {}
    status = data_block.get("status") or data_block.get("task_status") or "unknown"
    video_url = data_block.get("video_url") or data_block.get("download_url")

    return HeygenStatusResponse(job_id=video_id, status=status, video_url=video_url, raw=data)
