FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-local.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set INSTALL_LOCAL_MODEL=true for a self-contained no-secret image using BLIP.
# This increases image size/build time, but avoids API keys during evaluation.
ARG INSTALL_LOCAL_MODEL=false
ARG LOCAL_MODEL_ID=Salesforce/blip-image-captioning-base
RUN if [ "$INSTALL_LOCAL_MODEL" = "true" ]; then \
      pip install --no-cache-dir -r requirements-local.txt && \
      python - <<PY \
from transformers import BlipProcessor, BlipForConditionalGeneration; \
model_id = "${LOCAL_MODEL_ID}"; \
BlipProcessor.from_pretrained(model_id); \
BlipForConditionalGeneration.from_pretrained(model_id); \
print(f"Downloaded local caption model: {model_id}") \
PY \
    ; fi

COPY . .

CMD ["python", "-m", "src.main"]
