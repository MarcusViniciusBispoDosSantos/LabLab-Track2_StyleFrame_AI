from __future__ import annotations

from PIL import Image

from src.config import Settings
from src.heuristics import compute_signals, merge_frame_captions

_PROCESSOR = None
_MODEL = None


def _load_model(settings: Settings):
    global _PROCESSOR, _MODEL
    if _PROCESSOR is not None and _MODEL is not None:
        return _PROCESSOR, _MODEL
    try:
        import torch
        from transformers import BlipForConditionalGeneration, BlipProcessor
    except Exception as exc:
        raise RuntimeError("Local BLIP dependencies are not installed. Build with INSTALL_LOCAL_MODEL=true.") from exc

    _PROCESSOR = BlipProcessor.from_pretrained(settings.local_model_id)
    _MODEL = BlipForConditionalGeneration.from_pretrained(settings.local_model_id)
    _MODEL.eval()
    return _PROCESSOR, _MODEL


def describe_with_local_blip(frames: list[Image.Image], metadata: dict, settings: Settings) -> str:
    processor, model = _load_model(settings)
    try:
        import torch
    except Exception as exc:
        raise RuntimeError("PyTorch is required for local_blip backend") from exc

    frame_captions: list[str] = []
    # Use up to 5 frames for accuracy/runtime balance on CPU.
    for img in frames[: min(len(frames), 5)]:
        inputs = processor(images=img.convert("RGB"), return_tensors="pt")
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=28, num_beams=3)
        caption = processor.decode(out[0], skip_special_tokens=True).strip()
        if caption:
            frame_captions.append(caption)
    signals = compute_signals(frames)
    return merge_frame_captions(frame_captions, signals, metadata)
