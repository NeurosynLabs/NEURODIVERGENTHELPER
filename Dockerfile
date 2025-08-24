# -------------------------------
# NeurodivergentHelper CPU Dockerfile (Updated)
# -------------------------------

# Base image with Python 3.12
FROM python:3.12-slim

# Set non-interactive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

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
RUN pip install --no-cache-dir -r requirements.txt

# --- Pre-cache models (optional) ---
# RUN python3 -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('NousResearch/Nous-Hermes-CPU'); AutoModelForCausalLM.from_pretrained('NousResearch/Nous-Hermes-CPU')"

# --- Expose ports ---
# FastAPI default: 8000
# Gradio default: 7860
EXPOSE 8000
EXPOSE 7860

# --- Environment variables ---
ENV HF_TOKEN=""
ENV PROMPT_URL="https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/NeurodivergentHelper.prompt.yml"
ENV MODEL_NAME=""
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=4

# --- Health check ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# --- Create non-root user for security ---
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# --- Default entrypoint ---
# Option: run FastAPI + Gradio integrated
CMD ["python3", "app.py"]
