# -------------------------------
# NeurodivergentHelper CPU Dockerfile
# -------------------------------

# Base image with Python 3.13
FROM python:3.13-slim

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

# --- Expose ports ---
EXPOSE 8000
EXPOSE 7860

# --- Environment variables ---
ENV HF_TOKEN=""
ENV PROMPT_URL="https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/prompt.txt"

# --- Default entrypoint ---
CMD ["python3", "app.py"]EXPOSE 8000
EXPOSE 7860

# --- Environment variables ---
# HF_TOKEN should be provided at runtime (docker run -e HF_TOKEN=...)
ENV HF_TOKEN=""
ENV PROMPT_URL="https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/prompt.txt"

# --- Default entrypoint ---
# Option 1: run FastAPI
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Option 2: run Gradio (uncomment if preferred)
CMD ["python3", "app.py"]
