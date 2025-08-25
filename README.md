# NeurodivergentHelper – Lightweight CPU Version

**Addressed to:** Chuck Merriman and Kyle Schneider  
**Website Integration:** https://neurodivergentexperiences.com  
**Purpose:** Free CPU-optimized version of NeurodivergentHelper designed for local testing and deployment. A paid version with extended capabilities, GPU support, advanced memory management, and premium modules is under development.

The CPU version is intended for self-hosting on Windows, macOS, or Linux. GPU-accelerated features are only available in Linux environments with a CUDA-compatible NVIDIA GPU.

---

## Overview

NeurodivergentHelper is an advanced emotional intelligence and linguistic support system tailored to neurodivergent individuals. It leverages context-aware processing, trauma-informed design, and sensory-aware interactions to provide safe, responsive, and adaptive support for complex emotional, social, and cognitive needs.

**Key Capabilities:**

- **Cognitive and Emotional Support:** Offers reframing techniques, emotional regulation guidance, mindfulness exercises, and strategies for internal system harmony.  
- **Neurotype-Specific Assistance:** Supports autistic, ADHD, SPD, and trauma-affected users with sensitive handling of emotional cues.  
- **Adaptive Session Memory:** Tracks the last 5 user interactions to ensure context-aware responses.  
- **Embeddable Chat Interface:** Easily integrated into websites via the `/embed` endpoint.  
- **FastAPI Endpoints:** Provides flexible API endpoints for custom frontend development and integrations.  
- **Open-Ended Extensibility:** Can be extended for Discord, Replit, and other platforms, with modular overrides and configuration.

**Alpha Deployments:**

- Poe: [NeurodivergentCalm](https://poe.com/NeurodivergentCalm)  
- Facebook Messenger: [Messenger Bot](https://m.me/1944934973012617?is_ai=1)  

---

## System Requirements

**CPU Version (Lightweight)**

- OS: Windows 10/11, macOS, or Linux  
- RAM: 8 GB minimum, 16 GB recommended  
- Disk: ~2 GB for dependencies, cache, and models  

**GPU Version (Future / Replit)**

- GPU: NVIDIA CUDA-compatible (12.1)  
- VRAM: 6–8 GB minimum  
- OS: Linux preferred for full GPU support  

> Note: GPU passthrough on Windows is not supported. Linux with CUDA is required for GPU execution.

---

## File Structure

```

NeurodivergentHelper/
├─ app.py                  # FastAPI + Gradio integration
├─ models.py               # CPU-optimized model loader
├─ requirements.txt        # Python dependencies
├─ Dockerfile              # Container configuration for CPU execution
├─ .gitignore              # Ignore cache, temporary files, and virtual environments
├─ NeurodivergentHelper.prompt.yml  # YAML system prompt
├─ README.md               # This documentation
└─ overrides/              # Optional custom app.py or Dockerfile overrides

````

### Key Files

- **`app.py`** – Entrypoint handling API and Gradio interface. Supports `/query`, `/embed`, and `/docs`.  
- **`models.py`** – Handles dynamic CPU-optimized model loading, caching, and device management.  
- **`requirements.txt`** – All Python dependencies required for CPU-based execution, including `transformers` and `pyyaml`.  
- **`Dockerfile`** – Docker container setup optimized for CPU deployment with pre-configured environment variables and thread settings.  
- **`NeurodivergentHelper.prompt.yml`** – YAML-based system prompt configuration for NeurodivergentHelper.  
- **`.gitignore`** – Excludes temporary files, caches, virtual environments, and model downloads to keep repository clean.  

---

## Website Integration

NeurodivergentHelper provides a versatile interface for embedding or API-driven integrations.

### 1. Direct iframe Embedding

```html
<iframe 
    src="https://your-domain.com/embed" 
    width="600" 
    height="500"
    frameborder="0"
    title="NeurodivergentHelper Chat">
</iframe>
````

### 2. API Integration for Custom Frontends

```javascript
const response = await fetch('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: userMessage })
});
const data = await response.json();
console.log(data.response);
```

**Available Endpoints:**

* `/` – API status and model information
* `/embed` – Embeddable chat interface
* `/query` – Chat API endpoint
* `/docs` – FastAPI documentation

---

## Configuration

### 1. Hugging Face Token (Mandatory for Model Downloads)

**Linux / WSL / macOS:**

```bash
export HF_TOKEN="your_token_here"
export MODEL_NAME="username/custom-model"  # Optional
```

**Windows PowerShell:**

```powershell
$env:HF_TOKEN="your_token_here"
$env:MODEL_NAME="username/custom-model"  # Optional
```

**Windows Command Prompt (cmd.exe):**

```cmd
set HF_TOKEN=your_token_here
set MODEL_NAME=username/custom-model  # Optional
```

**Docker Run (cross-platform):**

```bash
docker run -it --rm -p 8000:8000 -p 7860:7860 -e HF_TOKEN=your_token_here neurodivergenthelper
```

> 💡 **Tip:** On Windows PowerShell, using `-e HF_TOKEN=$env:HF_TOKEN` in Docker ensures the token passes into the container.

---

## CPU Model Recommendations

| Model Name                  | Description                              | CPU Performance |
| --------------------------- | ---------------------------------------- | --------------- |
| `microsoft/DialoGPT-small`  | Optimized for conversational flow        | Recommended     |
| `EleutherAI/gpt-neo-125M`   | Small GPT-Neo variant, fast on CPU       | Good            |
| `distilgpt2`                | Very small GPT-2 variant, minimal memory | Basic/Fast      |
| `microsoft/DialoGPT-medium` | Larger, higher-quality model, slower     | Fallback        |
| `MODEL_NAME` (env var)      | Custom user-defined Hugging Face model   | Depends on size |

---

## Running with Docker Desktop (CPU)

1. Clone repository:

```powershell
git clone https://github.com/NeurosynLabs/NeurodivergentHelper.git C:\NeurodivergentHelper
cd C:\NeurodivergentHelper
```

2. (Optional) Override `app.py` or `Dockerfile`:

```powershell
Copy-Item "C:\Overrides\app.py" -Destination ".\app.py" -Force
Copy-Item "C:\Overrides\Dockerfile" -Destination ".\Dockerfile" -Force
```

3. Build Docker image:

```powershell
docker build -t neurodivergenthelper .
```

4. Run container:

```powershell
docker run -it --rm -p 8000:8000 -p 7860:7860 -e HF_TOKEN=your_token_here neurodivergenthelper
```

**Access:**

* FastAPI + Embeddable Chat: `http://localhost:7860`
* API Documentation: `http://localhost:7860/docs`
* Embed Interface: `http://localhost:7860/embed`

---

## Quick One-Line Docker Run

```powershell
if (Test-Path "C:\NeurodivergentHelper") { cd C:\NeurodivergentHelper; git reset --hard; git clean -fd; git pull origin main } else { git clone https://github.com/NeurosynLabs/NeurodivergentHelper.git C:\NeurodivergentHelper; cd C:\NeurodivergentHelper }; docker build -t neurodivergenthelper .; docker run -it --rm -p 7860:7860 -e HF_TOKEN=your_token_here neurodivergenthelper
```

> Access `http://localhost:7860/embed` for the embeddable chat interface.

---

## Hosting Alternatives

* Docker Desktop (CPU) – Recommended for Windows.
* Hugging Face Spaces – Free hosting with Gradio interface (slower).
* Replit GPU – Development/testing; subscription required.
* Railway/Render – Cloud CPU hosting alternatives.
* Cloudflare Tunnel + DuckDNS – Optional subdomain exposure for local container.

> GPU passthrough on Windows WSL2 or VMware is not supported.

---

## Known Limitations

* CPU-only version slower than GPU.
* Session memory limited to last 5–10 exchanges.
* Some Hugging Face models may require more RAM.
* YAML parsing requires `pyyaml`.
* Free CPU version intended for local testing only.

---

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Set Hugging Face token
export HF_TOKEN="your_token_here"  # Linux/macOS/WSL
$env:HF_TOKEN="your_token_here"    # PowerShell
set HF_TOKEN=your_token_here       # CMD

# Optional: specify custom model
export MODEL_NAME="microsoft/DialoGPT-small"

# Run locally
python app.py
```

**Access points:**

* Main Interface: `http://localhost:7860`
* Embeddable Chat: `http://localhost:7860/embed`
* API Docs: `http://localhost:7860/docs`

---

## Troubleshooting

* `RuntimeError: No CPU models could be loaded!` → Ensure `HF_TOKEN` is set and model is available.
* `ModuleNotFoundError: No module named 'yaml'` → Install `pyyaml`.
* Slow responses → Use smaller models (`distilgpt2`) or increase CPU threads.
* CORS errors in iframe → Check CORS middleware in `app.py`.
* Gradio port conflicts → Adjust `server_port` in `app.py`.

**CPU Thread Optimization:**

```bash
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
```

---

## Development Notes

**Recent Enhancements:**

* YAML prompt loading from GitHub
* CPU performance optimizations
* Built-in embeddable chat interface (`/embed`)
* Session management with memory cleanup
* CORS support for iframe embedding
* Better error handling and fallbacks

**Planned Features:**

* Redis session storage
* Model caching and warm-up
* Rate limiting and authentication
* Advanced prompt templating

---

## Feedback & Contribution

* Email: [neurosynlabs@proton.me](mailto:neurosynlabs@proton.me), [NeurosynLabs@google.com](mailto:NeurosynLabs@google.com)
* Website: [https://neurodivergentexperiences.com](https://neurodivergentexperiences.com)

---

## License

**Proprietary – All Rights Reserved**

```
Copyright (c) 2025 NeurosynLabs. All rights reserved.
This software and its associated files are proprietary.  
No part may be reproduced, modified, distributed, or sold without written permission.
```

* Free CPU version for local testing only.
* Paid version features and modules restricted via tokens and environment variables.

---

## Developer Info

**Developer:** Jarred Gainer
**Emails:** [neurosynlabs@proton.me](mailto:neurosynlabs@proton.me), [NeurosynLabs@google.com](mailto:NeurosynLabs@google.com)

```

---

If you want, I can **also update your README with an explicit "Windows Docker Token Instructions" section** so anyone running PowerShell won’t get `export: command not found`. That would fully prevent the token confusion. Do you want me to do that?
