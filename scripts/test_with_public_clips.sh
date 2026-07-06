#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-track2-styleframe-ai:local}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p input output
cp samples/tasks_public_examples.json input/tasks.json
rm -f output/results.json

docker buildx build --platform linux/amd64 -t "$IMAGE_NAME" --load .

docker run --rm \
  -e CAPTION_BACKEND="${CAPTION_BACKEND:-heuristic}" \
  -e FRAME_SAMPLE_COUNT="${FRAME_SAMPLE_COUNT:-4}" \
  -v "$PWD/input:/input" \
  -v "$PWD/output:/output" \
  "$IMAGE_NAME"

python scripts/validate_results.py input/tasks.json output/results.json
cat output/results.json
