#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np


def create_video(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    width, height, fps, frames = 640, 360, 12, 72
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(path, fourcc, fps, (width, height))
    if not out.isOpened():
        raise RuntimeError("Could not create synthetic mp4")
    for i in range(frames):
        img = np.zeros((height, width, 3), dtype=np.uint8)
        # Blue/orange gradient background.
        img[:, :, 0] = np.linspace(80, 180, width, dtype=np.uint8)
        img[:, :, 1] = 80
        img[:, :, 2] = np.linspace(30, 220, width, dtype=np.uint8)
        # Moving "subject" circle.
        x = 80 + int(i * (width - 160) / max(frames - 1, 1))
        cv2.circle(img, (x, height // 2), 45, (40, 230, 90), -1)
        cv2.rectangle(img, (420, 90), (590, 260), (30, 30, 30), -1)
        cv2.putText(img, "TRACK 2", (438, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(img, "SYNTHETIC TEST", (405, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        out.write(img)
    out.release()
    print(f"created {path}")


if __name__ == "__main__":
    create_video(sys.argv[1] if len(sys.argv) > 1 else "/input/test_clip.mp4")
