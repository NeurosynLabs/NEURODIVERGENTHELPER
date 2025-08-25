# ===========================
# NeurodivergentHelper Dockerfile
# ===========================

# Base image (CPU-friendly)
FROM python:3.11-slim

# --- Environment variables ---
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface
ENV HF_TOKEN=""  # Pass your HF token at runtime

# --- System dependencies ---
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- Set working directory ---
WORKDIR /app

# --- Copy project files ---
COPY . /app

# --- Install Python dependencies ---
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        fastapi \
        uvicorn[standard] \
        transformers \
        torch \
        pyyaml \
        gradio

# --- Expose API port ---
EXPOSE 8000

# --- Default command to run FastAPI ---
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
