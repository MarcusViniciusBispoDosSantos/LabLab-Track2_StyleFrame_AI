#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-track2-styleframe-ai:local}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p input output
cat > input/tasks.json <<'JSON'
[
  {
    "task_id": "synthetic1",
    "video_url": "file:///input/test_clip.mp4",
    "styles": ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
  }
]
JSON

rm -f output/results.json

docker buildx build --platform linux/amd64 -t "$IMAGE_NAME" --load .

docker run --rm \
  -e CAPTION_BACKEND=heuristic \
  -e FRAME_SAMPLE_COUNT=4 \
  -v "$PWD/input:/input" \
  -v "$PWD/output:/output" \
  --entrypoint sh \
  "$IMAGE_NAME" \
  -lc "python scripts/create_synthetic_video.py /input/test_clip.mp4 && python -m src.main"

python scripts/validate_results.py input/tasks.json output/results.json
cat output/results.json
