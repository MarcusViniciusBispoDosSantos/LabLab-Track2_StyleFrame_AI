from __future__ import annotations

from src.api_vision import describe_with_vision_api
from src.config import Settings
from src.heuristics import heuristic_description
from src.local_blip import describe_with_local_blip
from src.video_io import FrameSet


def describe_video(frame_set: FrameSet, settings: Settings) -> tuple[str, str]:
    """Return (description, backend_used). Never raises for model errors; falls back to heuristic."""
    backend = settings.backend

    if backend in {"auto", "api", "vision_api"} and settings.vision_api_key:
        try:
            return describe_with_vision_api(frame_set.frames, frame_set.metadata, settings), "vision_api"
        except Exception as exc:
            print(f"[warn] vision_api failed; falling back: {exc}", flush=True)
            if backend in {"api", "vision_api"}:
                # Explicit API mode should still produce output instead of crashing the whole submission.
                pass

    if backend in {"auto", "local", "local_blip", "blip"}:
        try:
            return describe_with_local_blip(frame_set.frames, frame_set.metadata, settings), "local_blip"
        except Exception as exc:
            print(f"[warn] local_blip unavailable; falling back: {exc}", flush=True)
            if backend in {"local", "local_blip", "blip"}:
                pass

    description, _details = heuristic_description(frame_set.frames, frame_set.metadata)
    return description, "heuristic"
