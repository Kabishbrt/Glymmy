FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency specs first (layer caching)
COPY pyproject.toml ./

# Install deps — no project install yet
RUN uv pip install --system \
    fastapi \
    "uvicorn[standard]" \
    pydantic \
    pydantic-settings \
    loguru \
    ollama \
    anthropic \
    pandas \
    numpy \
    scikit-learn \
    python-multipart \
    httpx \
    chromadb \
    sentence-transformers \
    pillow \
    "qrcode[pil]" \
    "pyjwt[crypto]" \
    "strawberry-graphql[fastapi]"

# Copy the application source
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
