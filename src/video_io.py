from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import cv2
import numpy as np
import requests
from PIL import Image

from src.config import Settings


@dataclass
class FrameSet:
    video_path: str
    frames: list[Image.Image]
    frame_paths: list[str]
    metadata: dict


def _download_video(url: str, settings: Settings) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix or ".mp4"
    fd, target = tempfile.mkstemp(prefix="track2_video_", suffix=suffix)
    os.close(fd)
    max_bytes = settings.max_video_mb * 1024 * 1024
    with requests.get(url, stream=True, timeout=settings.download_timeout_seconds) as response:
        response.raise_for_status()
        total = 0
        with open(target, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(f"Video exceeds MAX_VIDEO_MB={settings.max_video_mb}")
                f.write(chunk)
    return target


def resolve_video(video_url: str, settings: Settings) -> str:
    parsed = urlparse(video_url)
    if parsed.scheme in {"http", "https"}:
        return _download_video(video_url, settings)
    if parsed.scheme == "file":
        return parsed.path
    if Path(video_url).exists():
        return video_url
    raise ValueError(f"Unsupported or unavailable video_url: {video_url}")


def _pil_from_bgr(frame: np.ndarray, max_side: int = 768) -> Image.Image:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)))
    return img


def extract_frames(video_url: str, settings: Settings) -> FrameSet:
    video_path = resolve_video(video_url, settings)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_url}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = frame_count / fps if fps > 0 and frame_count > 0 else 0.0

    n = max(1, settings.frame_sample_count)
    if frame_count > 0:
        # Avoid first/last exact frames; sample across full content.
        positions = np.linspace(0.08, 0.92, n)
        indices = sorted(set(int(p * max(frame_count - 1, 1)) for p in positions))
    else:
        indices = list(range(n))

    frames: list[Image.Image] = []
    frame_paths: list[str] = []
    temp_dir = tempfile.mkdtemp(prefix="track2_frames_")

    for idx in indices:
        if frame_count > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        img = _pil_from_bgr(frame)
        path = os.path.join(temp_dir, f"frame_{idx}.jpg")
        img.save(path, quality=85)
        frames.append(img)
        frame_paths.append(path)
    cap.release()

    if not frames:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError(f"No frames extracted from video: {video_url}")

    metadata = {
        "frame_count": frame_count,
        "fps": fps,
        "width": width,
        "height": height,
        "duration_seconds": round(duration, 2),
        "sampled_frames": len(frames),
        "source_url": video_url,
    }
    return FrameSet(video_path=video_path, frames=frames, frame_paths=frame_paths, metadata=metadata)
