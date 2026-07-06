from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


@dataclass(frozen=True)
class Settings:
    input_path: str = os.getenv("INPUT_PATH", "/input/tasks.json")
    output_path: str = os.getenv("OUTPUT_PATH", "/output/results.json")
    backend: str = os.getenv("CAPTION_BACKEND", "auto").strip().lower()
    frame_sample_count: int = int(os.getenv("FRAME_SAMPLE_COUNT", "6"))
    download_timeout_seconds: int = int(os.getenv("DOWNLOAD_TIMEOUT_SECONDS", "60"))
    max_video_mb: int = int(os.getenv("MAX_VIDEO_MB", "250"))
    vision_api_key: str | None = os.getenv("VISION_API_KEY")
    vision_base_url: str = os.getenv("VISION_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    vision_model: str = os.getenv("VISION_MODEL", "gpt-4o-mini")
    local_model_id: str = os.getenv("LOCAL_MODEL_ID", "Salesforce/blip-image-captioning-base")
    allow_synthetic_fallback: bool = os.getenv("ALLOW_SYNTHETIC_FALLBACK", "1") not in {"0", "false", "False"}


def get_settings() -> Settings:
    return Settings()
