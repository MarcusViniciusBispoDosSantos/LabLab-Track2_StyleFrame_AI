# StyleFrame AI — Track 2 Video Captioning Agent

StyleFrame AI is a Dockerized video captioning agent for **AMD Developer Hackathon ACT II — Track 2**.

It reads video captioning tasks from `/input/tasks.json`, analyzes each video, generates captions in the requested styles, and writes `/output/results.json` before exiting.

## Recommended GitHub repository

**Repository name:**

```text
StyleFrame-AI-Track2
```

**Repository description:**

```text
Dockerized video captioning agent for AMD Developer Hackathon Track 2. Samples video frames, analyzes visual content, and generates formal, sarcastic, humorous_tech, and humorous_non_tech captions.
```

## Track 2 contract

### Input

The container reads:

```text
/input/tasks.json
```

Example:

```json
[
  {
    "task_id": "v1",
    "video_url": "https://storage.example.com/clips/clip1.mp4",
    "styles": ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
  }
]
```

### Output

The container writes:

```text
/output/results.json
```

Example:

```json
[
  {
    "task_id": "v1",
    "captions": {
      "formal": "...",
      "sarcastic": "...",
      "humorous_tech": "...",
      "humorous_non_tech": "..."
    }
  }
]
```

## Architecture

```text
/input/tasks.json
      ↓
Download video URL
      ↓
Sample frames across the clip
      ↓
Analyze frames using one of three backends
      ↓
Generate captions for each requested style
      ↓
/output/results.json
```

## Caption backends

StyleFrame AI supports three modes.

### 1. `heuristic`

No API key required. Uses OpenCV frame sampling, color/motion/scene heuristics, and deterministic style writing.

Best for:

- online contract tests
- no-secret testing
- validating Docker behavior

```bash
CAPTION_BACKEND=heuristic
```

### 2. `local_blip`

No API key required. Uses a local image captioning model to caption sampled frames, then converts the summarized visual content into the required styles.

Best for:

- stronger no-secret competition submission
- public Docker image without embedded credentials

Build with:

```bash
docker buildx build \
  --platform linux/amd64 \
  --build-arg INSTALL_LOCAL_MODEL=true \
  --tag your-image:latest \
  --push \
  .
```

Run with:

```bash
CAPTION_BACKEND=local_blip
```

### 3. `vision_api`

Uses an OpenAI-compatible vision API if you provide your own credentials.

Best for:

- strongest caption accuracy if you have a reliable vision model API
- private testing or hosted execution where secrets are safely injected

Environment variables:

```env
CAPTION_BACKEND=vision_api
VISION_API_KEY=your_key
VISION_BASE_URL=https://api.openai.com/v1
VISION_MODEL=gpt-4o-mini
```

Do not commit real API keys.

## Local Docker test

From the project root:

```bash
./scripts/test_with_synthetic.sh
```

This builds a `linux/amd64` image, creates a synthetic test video inside the container, runs the Track 2 container contract, and validates `/output/results.json`.

## Test with public example clips

```bash
./scripts/test_with_public_clips.sh
```

This uses the public sample clips from the participant guide.

## GitHub Actions online test

This repository includes:

```text
.github/workflows/track2-online-check.yml
```

After pushing to GitHub:

1. Open your repository.
2. Go to **Actions**.
3. Select **Track 2 Online Check**.
4. Click **Run workflow**.
5. Wait for green success.

The workflow confirms:

```text
Docker image builds
linux/amd64 architecture is used
/input/tasks.json is read
/output/results.json is written
results.json is valid JSON
all requested styles receive captions
.env is not included in the image
```

## Publish Docker image to GitHub Container Registry

This repository includes:

```text
.github/workflows/publish-track2-ghcr.yml
```

To publish:

1. Go to **Actions**.
2. Select **Publish Track 2 Docker Image to GHCR**.
3. Click **Run workflow**.
4. Choose `install_local_model=true` for the stronger no-key local BLIP image, or `false` for the faster lightweight image.
5. Run the workflow.

Expected final image format:

```text
ghcr.io/YOUR_GITHUB_USERNAME/styleframe-ai-track2:latest
```

After publishing, make the GHCR package public before submitting.

## Required linux/amd64 image

The judging VM runs `linux/amd64`, so the final image must include a `linux/amd64` manifest.

Use:

```bash
docker buildx build \
  --platform linux/amd64 \
  --tag your-image:latest \
  --push \
  .
```

The included GitHub Actions publish workflow already uses:

```yaml
platforms: linux/amd64
```

## Submission notes

For lablab.ai, use:

**Project title:**

```text
StyleFrame AI
```

**Short description:**

```text
A Dockerized Track 2 video captioning agent that samples video frames and generates captions in formal, sarcastic, humorous technical, and humorous non-technical styles.
```

**Technology tags:**

```text
Python, Docker, OpenCV, Video Captioning, AI Agent, Computer Vision, NLP, GitHub Actions
```

**Application URL:**

Use your public GitHub repository URL if the platform requires an `https://` URL.

**Docker image:**

Use your public GHCR image reference, for example:

```text
ghcr.io/YOUR_GITHUB_USERNAME/styleframe-ai-track2:latest
```
