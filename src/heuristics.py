from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image


@dataclass
class SceneSignals:
    brightness: float
    saturation: float
    green_ratio: float
    warm_ratio: float
    blue_ratio: float
    edge_density: float
    motion_hint: str
    scene_hint: str
    color_hint: str


def _np_rgb(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGB"), dtype=np.uint8)


def compute_signals(frames: list[Image.Image]) -> SceneSignals:
    if not frames:
        return SceneSignals(0.5, 0.4, 0.2, 0.2, 0.2, 0.1, "gentle movement", "general scene", "balanced colors")

    brightness_vals, sat_vals, green_vals, warm_vals, blue_vals, edge_vals = [], [], [], [], [], []
    prev_gray = None
    motion_vals = []

    for img in frames:
        rgb = _np_rgb(img)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        h = hsv[:, :, 0].astype(np.float32)
        s = hsv[:, :, 1].astype(np.float32) / 255.0
        v = hsv[:, :, 2].astype(np.float32) / 255.0
        brightness_vals.append(float(np.mean(v)))
        sat_vals.append(float(np.mean(s)))
        green_vals.append(float(np.mean((h > 35) & (h < 95) & (s > 0.2))))
        warm_vals.append(float(np.mean(((h < 25) | (h > 165)) & (s > 0.18))))
        blue_vals.append(float(np.mean((h > 90) & (h < 135) & (s > 0.18))))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 80, 160)
        edge_vals.append(float(np.mean(edges > 0)))
        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            motion_vals.append(float(np.mean(diff)) / 255.0)
        prev_gray = gray

    brightness = float(np.mean(brightness_vals))
    saturation = float(np.mean(sat_vals))
    green_ratio = float(np.mean(green_vals))
    warm_ratio = float(np.mean(warm_vals))
    blue_ratio = float(np.mean(blue_vals))
    edge_density = float(np.mean(edge_vals))
    motion = float(np.mean(motion_vals)) if motion_vals else 0.03

    if motion > 0.16:
        motion_hint = "active movement and noticeable scene changes"
    elif motion > 0.07:
        motion_hint = "moderate motion across the clip"
    else:
        motion_hint = "slow, steady movement"

    if green_ratio > 0.32:
        scene_hint = "outdoor nature or garden scene"
    elif edge_density > 0.15 and brightness < 0.45:
        scene_hint = "structured indoor or technology-heavy scene"
    elif warm_ratio > 0.30 and green_ratio > 0.12:
        scene_hint = "outdoor street or landscape with warm tones"
    elif blue_ratio > 0.28:
        scene_hint = "cool-toned sky, water, screen, or indoor scene"
    elif edge_density > 0.12:
        scene_hint = "urban, office, or built environment"
    else:
        scene_hint = "everyday visual scene"

    dominant = max((green_ratio, "green/natural tones"), (warm_ratio, "warm/orange tones"), (blue_ratio, "cool/blue tones"), key=lambda x: x[0])[1]
    if saturation < 0.18:
        color_hint = "muted colors"
    elif brightness < 0.28:
        color_hint = f"dark lighting with {dominant}"
    elif brightness > 0.72:
        color_hint = f"bright lighting with {dominant}"
    else:
        color_hint = f"balanced lighting with {dominant}"

    return SceneSignals(brightness, saturation, green_ratio, warm_ratio, blue_ratio, edge_density, motion_hint, scene_hint, color_hint)


def merge_frame_captions(frame_captions: list[str], signals: SceneSignals, metadata: dict) -> str:
    cleaned = [c.strip().rstrip(".") for c in frame_captions if c and c.strip()]
    if cleaned:
        # Prefer recurring details, but keep it short and not overfit to one frame.
        joined = "; ".join(cleaned[:4])
        return f"A video showing {joined}, with {signals.motion_hint} and {signals.color_hint}."
    duration = metadata.get("duration_seconds")
    duration_text = f" over about {duration} seconds" if duration else ""
    return f"A {signals.scene_hint}{duration_text}, shown with {signals.motion_hint} and {signals.color_hint}."


def heuristic_description(frames: list[Image.Image], metadata: dict) -> tuple[str, dict]:
    signals = compute_signals(frames)
    description = merge_frame_captions([], signals, metadata)
    return description, {"signals": signals.__dict__, "metadata": metadata}
