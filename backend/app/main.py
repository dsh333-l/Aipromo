from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    GenerateVideoRequest,
    GenerateVideoResponse,
    ProductAnalysisRequest,
    ProductAnalysisResponse,
    HeygenStatusResponse,
)
from .services.ai import analyze_product, generate_video_script
from .services.video import ASSETS_DIR, generate_video_assets, check_heygen_status


app = FastAPI(
    title="aiPromo Demo API",
    description="Demo backend providing AI-driven marketing analysis and auto video generation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/generated", StaticFiles(directory=ASSETS_DIR), name="generated")


@app.post("/api/analyze", response_model=ProductAnalysisResponse)
def analyze(req: ProductAnalysisRequest) -> ProductAnalysisResponse:
    return analyze_product(req)


@app.post("/api/generate_script", response_model=GenerateScriptResponse)
def script(req: GenerateScriptRequest) -> GenerateScriptResponse:
    script = generate_video_script(req)
    return GenerateScriptResponse(script=script)


@app.post("/api/generate_video", response_model=GenerateVideoResponse)
def video(req: GenerateVideoRequest) -> GenerateVideoResponse:
    try:
        video_path, audio_path, job_id = generate_video_assets(req)
    except Exception as exc:  # pragma: no cover - logging stub
        raise HTTPException(status_code=500, detail=f"视频生成失败: {exc}") from exc

    video_url = video_path if isinstance(video_path, str) else f"/generated/{video_path.name}"
    audio_url = audio_path if isinstance(audio_path, str) else f"/generated/{audio_path.name}"

    return GenerateVideoResponse(
        video_url=video_url,
        audio_url=audio_url,
        job_id=job_id,
        status="queued" if job_id else None,
    )


@app.get("/api/video_status", response_model=HeygenStatusResponse)
def video_status(video_id: str) -> HeygenStatusResponse:
    return check_heygen_status(video_id)
