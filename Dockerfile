# -------------------------------
# NeurodivergentHelper CPU Dockerfile (Dynamic Model Download)
# -------------------------------

FROM python:3.12-slim

# Non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# --- Install system dependencies ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        wget \
        build-essential \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# --- Set working directory ---
WORKDIR /app

# --- Copy project files ---
COPY . /app

# --- Install Python dependencies ---
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# --- Expose FastAPI & Gradio ports ---
EXPOSE 8000
EXPOSE 7860

# --- Environment variables ---
ENV HF_TOKEN=""
ENV PROMPT_URL="https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/NeurodivergentHelper.prompt.yml"
ENV MODEL_NAME=""  # Optional override for models.py
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=4
ENV TRANSFORMERS_NO_ADVISORY_WARNINGS=1

# --- Healthcheck ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# --- Non-root user ---
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# --- Entrypoint ---
CMD ["python3", "app.py"]
