# NeurodivergentHelper

NeurodivergentHelper is an advanced emotional intelligence and linguistic support system designed for neurodivergent individuals navigating complex emotional and social landscapes. It integrates trauma-informed and sensory-aware design principles, supporting cognitive reframing, emotional regulation, mindfulness, and internal system harmony.

This repository provides a **CPU-compatible setup**, making it easy to self-host on Windows, Linux, or WSL2 without GPU requirements.

---

## Features

- Supports multiple neurotypes (autistic, ADHD, SPD, trauma-affected)
- Implements evidence-based therapeutic modalities (CBT, DBT, ACT, IFS)
- FastAPI API for programmatic access
- Gradio UI for interactive chat
- Session memory with last 5 interactions
- Adaptive learning engine (session-level)
- Fully CPU-compatible, no GPU required

---

## System Requirements (CPU)

- **OS:** Windows 11, Linux, macOS, or WSL2
- **RAM:** 8 GB minimum (16+ GB recommended)
- **CPU:** Modern multi-core CPU (Intel i5/Ryzen 5 or better)
- **Disk:** 5 GB free for model and cache
- **GPU:** Optional — CPU-only setup supported

---

## Folder Structure

```
NeurodivergentHelper/
├── app.py
├── models.py
├── requirements.txt
├── Dockerfile
├── .gitignore
├── NeurodivergentHelper.txt
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/NeurosynLabs/NeurodivergentHelper.git
cd NeurodivergentHelper
```

### 2. Install dependencies (CPU-only)

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Hugging Face Token Setup (Secure)

1. **Create a Hugging Face account** if you don’t have one: [https://huggingface.co/join](https://huggingface.co/join)

2. **Generate an access token**:

   - Go to **Settings → Access Tokens → New Token**
   - Copy the generated token (keep it private!)

3. **Use the token securely**:

   **Option 1 (recommended): Environment variable**  

   Ensure `app.py` reads the token from the environment:

   ```python
   import os
   HF_TOKEN = os.environ.get("HF_TOKEN", "")
   ```

   Then set the environment variable:

   - **Linux/macOS:**
     ```bash
     export HF_TOKEN="your_generated_token_here"
     ```
   - **Windows CMD:**
     ```cmd
     set HF_TOKEN=your_generated_token_here
     ```
   - **PowerShell:**
     ```powershell
     $env:HF_TOKEN="your_generated_token_here"
     ```

   **Option 2 (placeholder in code)**

   Replace the variable in `app.py` with a placeholder (never your real token):

   ```python
   HF_TOKEN = "YOUR_HF_TOKEN_HERE"
   ```

   > ⚠️ Never commit your actual Hugging Face token to the repository. Always use environment variables in production or public repos.

Optionally, set the prompt URL:

```bash
export PROMPT_URL="https://raw.githubusercontent.com/NeurosynLabs/NeurodivergentHelper/main/NeurodivergentHelper.txt"
```

---

## Running Locally

### Option 1: FastAPI API

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Visit: `http://localhost:8000`

---

### Option 2: Gradio UI

```bash
python app.py
```

Visit: `http://localhost:7860`

---

## Docker (CPU-only)

### Build Docker image

```bash
docker build -t neurodivergenthelper:cpu .
```

### Run Docker container

```bash
docker run -it --rm -p 7860:7860 -e HF_TOKEN="your_generated_token_here" neurodivergenthelper:cpu
```

---

## Models

CPU-friendly recommended models:

- `EleutherAI/gpt-neo-125M` (default)
- `distilgpt2` (fallback)

Larger models may fail on CPU due to memory constraints.

### Optional: Model Override

Set the environment variable to use a different Hugging Face model:

```bash
export MODEL_NAME="EleutherAI/gpt-neo-125M"
```

Then restart the app. Make sure the model is CPU-friendly if not using a GPU.

---

## Session Memory

- Stores the last 5 exchanges per session.
- To clear session memory during runtime:

```python
from app import SESSION_MEMORY
SESSION_MEMORY.clear()
```

- Useful if context is getting too long or unwanted.

---

## Troubleshooting

- **Slow performance:** CPU inference is slower than GPU. Use smaller models.
- **Missing HF_TOKEN:** Ensure your Hugging Face token is set as an environment variable.
- **Port conflicts:** Change FastAPI (`8000`) or Gradio (`7860`) ports if already in use.
- **CUDA/GPU errors:** Ignore if CPU-only. For GPU, ensure PyTorch + CUDA versions match.

---

## Contributing

- Fork the repository and submit pull requests for improvements.
- Ensure no Hugging Face tokens or secrets are committed.
- Follow PEP8 formatting and comment code clearly.

---

## License

MIT License
