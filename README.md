# NeurodivergentHelper – Lightweight CPU Version

**Addressed to:** Chuck Merriman and Kyle Schneider  
**Website Integration:** https://neurodivergentexperiences.com  
**Purpose:** Intended to be embedded in the website via an iframe. This is the **free CPU version** of the prompt. A paid version with additional modules, settings, and features is under development. This system could also be extended to Discord (both free and paid versions).

Replit: GPU version works for development/testing; $200ish/year plan covers 1-year hosting: https://replit.com/pricing  

Alternative: OpenAI.

CPU version released to self-host due to GPU limitations on Windows. GPU version requires Linux and a CUDA-compatible GPU.

---

## Overview

NeurodivergentHelper is an advanced emotional intelligence and linguistic support system purpose-built for neurodivergent individuals navigating complex emotional and social landscapes. It is trauma-informed, sensory-aware, and designed to prioritize psychological safety and respect for neurodiversity.

**Capabilities:**

- Cognitive reframing, emotional regulation, mindfulness, and internal system harmony.
- Supports neurotypes including autistic, ADHD, SPD, and trauma-affected individuals.
- Sensitive emotional tone analysis, boundary negotiation, and interpersonal conflict guidance.
- Adaptive session memory tracks the last 5 user interactions for context-aware responses.
- Flexible integration for journaling, website, or web-based interfaces.

Alpha versions:

- On Poe: https://poe.com/NeurodivergentCalm  
- On Facebook Messenger: https://m.me/1944934973012617?is_ai=1

**Lightweight CPU Version Notes:**

- Runs entirely on CPU (`device = "cpu"`) due to GPU limitations on Windows.
- Slower responses expected compared to GPU-based models.
- Developer has yet to test all errors; project is open for feedback.

---

## System Requirements

**CPU Version (Lightweight)**

- OS: Windows 10/11, macOS, or Linux  
- RAM: 8 GB minimum, 16 GB recommended  
- Disk: 2 GB for dependencies and model cache  

**GPU Version (Future / Replit)**

- GPU: NVIDIA CUDA-compatible GPU (12.1)  
- VRAM: Minimum 6–8 GB  
- OS: Linux preferred for local GPU hosting  

---

## File Structure

```
NeurodivergentHelper/
├─ app.py
├─ models.py
├─ requirements.txt
├─ Dockerfile
├─ .gitignore
├─ NeurodivergentHelper.txt
├─ README.md
└─ overrides/  # optional custom app.py or Dockerfile
```

### Key Files

- `app.py` – FastAPI and Gradio integration; entrypoint for API and optional web interface.  
- `models.py` – Handles model loading and selection.  
- `requirements.txt` – All dependencies for CPU execution.  
- `Dockerfile` – Container setup (CPU-compatible).  
- `NeurodivergentHelper.txt` – System prompt text for the bot.  
- `.gitignore` – Excludes caches, virtual environments, and temporary files.  

---

## Configuration

1. **Hugging Face Token**  
   - Do **not** store HF_TOKEN in `app.py`.  
   - Create a token on Hugging Face and export it as an environment variable:  

```bash
export HF_TOKEN="your_token_here"
```

- `app.py` references it automatically for model downloads.

2. **Optional Custom Model**  
- Set `MODEL_NAME` environment variable if you want a different Hugging Face model:

```bash
export MODEL_NAME="username/custom-model"
```

3. **Optional .env File**

```bash
# .env example
HF_TOKEN=your_huggingface_token
MODEL_NAME=EleutherAI/gpt-neo-125M
```

---

## CPU Model Recommendations

Due to GPU limitations, the lightweight version is CPU-only. The following models are included in `models.py`:

| Model Name                  | Notes                                              | Performance on CPU |
|------------------------------|--------------------------------------------------|------------------|
| `EleutherAI/gpt-neo-125M`   | Small GPT-Neo model, fast on CPU                 | Recommended      |
| `distilgpt2`                 | Very small GPT-2 variant, minimal memory usage  | Slightly less capable |
| `MODEL_NAME` (optional env)  | Custom Hugging Face model defined by user       | Depends on model size |

**How it works:**  
- Tries models in order until one loads successfully.  
- Runs entirely on CPU (`device = "cpu"`).  
- Slower than GPU-based models for complex prompts.

---

## Running with Docker Desktop (Recommended)

1. Clone or update the repository:

```powershell
git clone https://github.com/NeurosynLabs/NeurodivergentHelper.git C:\NeurodivergentHelper
cd C:\NeurodivergentHelper
```

2. (Optional) Override `app.py` or `Dockerfile` by placing custom files in `C:\NeurodivergentHelper\overrides`:

```powershell
Copy-Item "C:\Overrides\app.py" -Destination ".\app.py" -Force
Copy-Item "C:\Overrides\Dockerfile" -Destination ".\Dockerfile" -Force
```

3. Build Docker image:

```powershell
docker build -t neurodivergenthelper .
```

4. Run Docker container:

```powershell
docker run -it --rm -p 8000:8000 -p 7860:7860 neurodivergenthelper
```

- FastAPI: `http://localhost:8000`  
- Gradio: `http://localhost:7860`

---

### Quick Start – One-Line Docker Desktop Run (Windows PowerShell)

```powershell
# Clone/update repo, build Docker image, and run container in one command
if (Test-Path "C:\NeurodivergentHelper") { cd C:\NeurodivergentHelper; git reset --hard; git clean -fd; git pull origin main } else { git clone https://github.com/NeurosynLabs/NeurodivergentHelper.git C:\NeurodivergentHelper; cd C:\NeurodivergentHelper }; docker build -t neurodivergenthelper .; docker run -it --rm -p 8000:8000 -p 7860:7860 neurodivergenthelper
```

> Open `http://localhost:8000` for API and `http://localhost:7860` for the web UI.  

---

## Hosting Alternatives

- **Docker Desktop (CPU)** – Recommended for Windows; works without special configuration.  
- **Replit GPU** – Development/testing; subscription required.  
- **Cloudflare Tunnel + DuckDNS** – Optional for exposing local CPU container via subdomain.  

> GPU passthrough on Windows WSL2, VMware, or native Windows is **not supported**. Linux + CUDA required for GPU execution.

---

## Known Limitations

- CPU-only version is slower than GPU models.  
- Session memory limited to last 5 prompts.  
- Some Hugging Face models may require more RAM.  
- Free CPU version intended for local testing only; GPU hosting requires Replit subscription.

---

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Set Hugging Face token
export HF_TOKEN="your_token_here"

# Optional: specify custom model
export MODEL_NAME="username/custom-model"

# Run locally with CPU
python app.py
```

- Access FastAPI: `http://localhost:8000`  
- Access Gradio (if launched): `http://localhost:7860`

---

## Troubleshooting

- `RuntimeError: No CPU models could be loaded!` → Ensure `HF_TOKEN` is set and model is available on Hugging Face.  
- Slow responses → Use smaller models (`distilgpt2`).  
- Gradio port conflicts → Change `server_port` in `app.py`.  

---

## Feedback & Contribution

This project is under active development. Feedback on errors, performance, or feature requests is welcome via:  
- Email: neurosynlabs@proton.me, NeurosynLabs@google.com  
- Website: https://neurodivergentexperiences.com  

---

## License

**Proprietary – All Rights Reserved**  

```
Copyright (c) 2025 NeurosynLabs. All rights reserved.

This software and its associated files are proprietary.  
No part of this software may be reproduced, modified, distributed, or sold without written permission from the copyright owner.
```

- Free CPU version may be used for local testing only.  
- Paid version features and modules are restricted; access controlled via tokens and environment variables.

---

## Developer Info

**Developer:** Jarred Gainer  
**Emails:** neurosynlabs@proton.me, NeurosynLabs@google.com
