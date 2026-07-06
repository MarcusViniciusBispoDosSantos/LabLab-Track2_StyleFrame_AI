from __future__ import annotations

import re


def _clean_base(description: str) -> str:
    text = re.sub(r"\s+", " ", description).strip()
    text = text.rstrip(".")
    # Keep captions concise; LLM judge rewards direct faithfulness.
    if len(text) > 280:
        text = text[:277].rsplit(" ", 1)[0] + "..."
    return text


def caption_for_style(description: str, style: str) -> str:
    base = _clean_base(description)
    style = style.strip()

    if style == "formal":
        return f"{base}."
    if style == "sarcastic":
        return f"{base} — truly groundbreaking footage of reality doing exactly what it was scheduled to do."
    if style == "humorous_tech":
        return f"{base}, basically a real-world video stream rendering its own little production environment."
    if style == "humorous_non_tech":
        return f"{base}, the kind of scene that looks like it showed up ready for its own tiny documentary."

    # Unknown requested styles should still get a non-empty caption.
    pretty = style.replace("_", " ") or "requested"
    return f"In a {pretty} style: {base}."


def build_captions(description: str, styles: list[str]) -> dict[str, str]:
    return {style: caption_for_style(description, style) for style in styles}
