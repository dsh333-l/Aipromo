from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

from ..models import GenerateVideoRequest


ASSETS_DIR = Path(__file__).resolve().parent.parent / "generated"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp_slug() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S%f")


def _write_placeholder(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def generate_video_assets(req: GenerateVideoRequest) -> Tuple[Path, Path]:
    """Generate placeholder files to keep the接口稳定, 后续可接入真实合成流程。"""
    script = req.script
    slug = _timestamp_slug()

    summary_lines = [
        f"视频风格: {req.video_style}",
        f"配音: {req.voice.language} · {req.voice.voice_style} · {req.voice.age_group}",
        "",
        "分镜脚本：",
    ]
    for scene in script.scenes:
        summary_lines.append(f"- {scene.title}: 画面={scene.visuals} | 旁白={scene.voice_over} | 字幕={scene.screen_text}")

    video_path = ASSETS_DIR / f"demo_video_{slug}.mp4"
    audio_path = ASSETS_DIR / f"demo_voice_{slug}.mp3"

    _write_placeholder(video_path, "\n".join(summary_lines))
    _write_placeholder(
        audio_path,
        "这是一个配音占位文件。后续可接入真实 TTS 输出。\n\n完整旁白：\n" + "\n".join(scene.voice_over for scene in script.scenes),
    )

    return video_path, audio_path
