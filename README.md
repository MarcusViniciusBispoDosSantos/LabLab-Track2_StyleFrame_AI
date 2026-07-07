# StyleFrame AI - Track 2 Video Captioning Agent

StyleFrame AI is a Dockerized video captioning agent for **AMD Developer Hackathon ACT II - Track 2**. It reads video captioning tasks from `/input/tasks.json`, analyzes each video, and writes style-specific captions to `/output/results.json`.

The project is designed for the Track 2 contract:

- Input path: `/input/tasks.json`
- Output path: `/output/results.json`
- Required output: one caption for every requested style
- Supported styles: `formal`, `sarcastic`, `humorous_tech`, `humorous_non_tech`
- Final image target: `linux/amd64`
- Public container image: `ghcr.io/marcusviniciusbispodossantos/styleframe-ai-track2:latest`


---

## Public Links

**Public GitHub Repository**

```text
https://github.com/MarcusViniciusBispoDosSantos/LabLab-Track2_StyleFrame_AI
```

**Application URL / Demo URL**

```text
https://github.com/MarcusViniciusBispoDosSantos/LabLab-Track2_StyleFrame_AI
```

**Docker Image Reference**

```text
ghcr.io/marcusviniciusbispodossantos/styleframe-ai-track2:latest
```

**Demo Application Platform**

```text
GitHub Container Registry / Docker
```

---

## Track 2 Input Format

The judging system runs the container with tasks mounted at `/input/tasks.json`.

```json
[
  {
    "task_id": "v1",
    "video_url": "https://example.com/video.mp4",
    "styles": ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
  }
]
```

---

## Track 2 Output Format

The container writes results to `/output/results.json` before exiting.

```json
[
  {
    "task_id": "v1",
    "captions": {
      "formal": "A concise, objective caption describing the video.",
      "sarcastic": "A dry, lightly ironic caption that still matches the video.",
      "humorous_tech": "A funny caption using light technology or programming references.",
      "humorous_non_tech": "A funny everyday caption with no technical jargon."
    }
  }
]
```

---

## Architecture

StyleFrame AI uses a modular video captioning pipeline:

1. **Task loader** - reads `/input/tasks.json`.
2. **Video downloader / frame sampler** - loads the video URL and samples frames across the clip.
3. **Visual analyzer** - extracts visual signals from the sampled frames.
4. **Scene summarizer** - creates a concise description of what happens in the video.
5. **Style writer** - generates captions for every requested style.
6. **Result writer** - writes valid JSON to `/output/results.json`.

The agent supports multiple backends:

- `heuristic` - no-secret fallback mode for online contract validation.
- `local_blip` - optional self-contained image captioning mode using a local BLIP model.
- `vision_api` - optional external vision API mode when secure credentials are available.

For final Track 2 submission, the recommended no-secret option is to publish with the local model enabled.

---

## Environment Variables

| Variable | Default | Description |
|---|---:|---|
| `CAPTION_BACKEND` | `heuristic` | Captioning backend: `heuristic`, `local_blip`, or `vision_api`. |
| `FRAME_SAMPLE_COUNT` | `8` | Number of frames to sample from each video. |
| `INPUT_PATH` | `/input/tasks.json` | Override input file path for local testing. |
| `OUTPUT_PATH` | `/output/results.json` | Override output file path for local testing. |
| `VISION_API_KEY` | empty | Optional API key for `vision_api` backend. Do not commit this. |
| `VISION_BASE_URL` | empty | Optional vision API base URL. |
| `VISION_MODEL` | empty | Optional vision-capable model name. |

Do not commit a real `.env` file. Use `.env.example` only.

---

## Online Validation with GitHub Actions

This repository includes an online check workflow:

```text
.github/workflows/track2-online-check.yml
```

Run it from:

```text
GitHub -> Actions -> Track 2 Online Check -> Run workflow
```

A green check confirms:

- Docker builds online.
- The image runs as `linux/amd64`.
- The container reads `/input/tasks.json`.
- The container writes `/output/results.json`.
- `results.json` is valid JSON.
- Every requested caption style is present.
- No `.env` file is included inside the image.

---

## Publish Docker Image to GHCR

Use the included publish workflow:

```text
.github/workflows/publish-track2-ghcr.yml
```

Run it from:

```text
GitHub -> Actions -> Publish Track 2 Docker Image to GHCR -> Run workflow
```

For final submission, use:

```text
install_local_model = true
```

Expected image:

```text
ghcr.io/marcusviniciusbispodossantos/styleframe-ai-track2:latest
```

After publishing, make the GHCR package public:

```text
GitHub repository -> Packages -> styleframe-ai-track2 -> Package settings -> Change visibility -> Public
```

---

## Manual Docker Build Command

If building manually, use the `linux/amd64` target:

```bash
docker buildx build \
  --platform linux/amd64 \
  --build-arg INSTALL_LOCAL_MODEL=true \
  --tag ghcr.io/marcusviniciusbispodossantos/styleframe-ai-track2:latest \
  --push \
  .
```

The final image must include a `linux/amd64` manifest because the judging VM uses `linux/amd64`.

---

## Example Judge-Style Run

```bash
mkdir -p input output

cat > input/tasks.json <<'JSON'
[
  {
    "task_id": "v1",
    "video_url": "https://example.com/video.mp4",
    "styles": ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
  }
]
JSON

docker run --rm \
  -e CAPTION_BACKEND=local_blip \
  -v "$PWD/input:/input" \
  -v "$PWD/output:/output" \
  ghcr.io/marcusviniciusbispodossantos/styleframe-ai-track2:latest

cat output/results.json
```

---

## Submission Notes for lablab.ai

Use the GitHub repository URL as the Application URL if the platform requires a browser URL. Use the GHCR image reference as the container image / Docker image reference.

**Application URL**

```text
https://github.com/MarcusViniciusBispoDosSantos/LabLab-Track2_StyleFrame_AI
```

**Docker Image Reference**

```text
ghcr.io/marcusviniciusbispodossantos/styleframe-ai-track2:latest
```

**Demo Application Platform**

```text
GitHub Container Registry / Docker
```

---

## Final Checklist

- [ ] GitHub repository is public.
- [ ] README includes setup and usage instructions.
- [ ] GitHub Actions online check is green.
- [ ] Docker image is published to GHCR.
- [ ] GHCR package visibility is public.
- [ ] Docker image includes a `linux/amd64` manifest.
- [ ] Container reads `/input/tasks.json`.
- [ ] Container writes `/output/results.json`.
- [ ] Output JSON includes captions for every requested style.
- [ ] No real `.env` or private API key is committed.
- [ ] Cover image, video presentation, and slide presentation are uploaded to lablab.ai.
