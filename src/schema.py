from __future__ import annotations

from typing import Any

REQUIRED_STYLES = ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]


def normalize_task(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Each task must be an object")
    task_id = str(raw.get("task_id", "")).strip()
    video_url = str(raw.get("video_url", "")).strip()
    styles = raw.get("styles") or REQUIRED_STYLES
    if not task_id:
        raise ValueError("Task is missing task_id")
    if not video_url:
        raise ValueError(f"Task {task_id} is missing video_url")
    if not isinstance(styles, list) or not styles:
        styles = REQUIRED_STYLES
    normalized_styles = []
    for style in styles:
        s = str(style).strip()
        if s and s not in normalized_styles:
            normalized_styles.append(s)
    return {"task_id": task_id, "video_url": video_url, "styles": normalized_styles or REQUIRED_STYLES}


def validate_results(results: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> None:
    if not isinstance(results, list):
        raise ValueError("results.json must contain a list")
    if len(results) != len(tasks):
        raise ValueError(f"Expected {len(tasks)} results, got {len(results)}")
    expected = {t["task_id"]: set(t["styles"]) for t in tasks}
    for result in results:
        task_id = result.get("task_id")
        if task_id not in expected:
            raise ValueError(f"Unexpected task_id in result: {task_id}")
        captions = result.get("captions")
        if not isinstance(captions, dict):
            raise ValueError(f"Result for {task_id} must include captions object")
        missing = expected[task_id] - set(captions.keys())
        if missing:
            raise ValueError(f"Result for {task_id} is missing captions for styles: {sorted(missing)}")
        for style, caption in captions.items():
            if not isinstance(caption, str) or not caption.strip():
                raise ValueError(f"Caption for {task_id}/{style} must be a non-empty string")
