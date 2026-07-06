from __future__ import annotations

import base64
import json
from io import BytesIO

import requests
from PIL import Image

from src.config import Settings


def _image_to_data_url(img: Image.Image) -> str:
    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=80)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def describe_with_vision_api(frames: list[Image.Image], metadata: dict, settings: Settings) -> str:
    if not settings.vision_api_key:
        raise RuntimeError("VISION_API_KEY is not set")

    # Keep payload small for speed and cost.
    selected = frames[: min(len(frames), 6)]
    content = [
        {
            "type": "text",
            "text": (
                "You are a video captioning assistant. These images are sampled frames from one video. "
                "Describe the video faithfully in one concise English sentence. Mention the main subject, setting, "
                "visible action, and overall visual context. Do not invent details not visible in the frames."
            ),
        }
    ]
    for img in selected:
        content.append({"type": "image_url", "image_url": {"url": _image_to_data_url(img)}})

    url = f"{settings.vision_base_url}/chat/completions"
    payload = {
        "model": settings.vision_model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.1,
        "max_tokens": 120,
    }
    headers = {
        "Authorization": f"Bearer {settings.vision_api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, json=payload, timeout=90)
    if response.status_code >= 400:
        raise RuntimeError(f"Vision API error {response.status_code}: {response.text[:400]}")
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise RuntimeError(f"Unexpected vision API response: {json.dumps(data)[:500]}") from exc
