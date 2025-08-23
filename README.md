# NeurodivergentHelper – Lightweight CPU Version

**Addressed to:** Chuck Merriman and Kyle Schneider  
**Website Integration:** https://neurodivergentexperiences.com  
**Purpose:** Intended to be embedded in the website via an iframe. This is the **free version** of the prompt. A paid version with additional modules, settings, and features is under development. This system could also be extended to Discord (both free and paid versions).

---

## Overview

NeurodivergentHelper is an advanced emotional intelligence and linguistic support system purpose-built for neurodivergent individuals navigating complex emotional and social landscapes. It is trauma-informed, sensory-aware, and designed to prioritize psychological safety and respect for neurodiversity.

**Capabilities:**

- Cognitive reframing, emotional regulation, mindfulness, and internal system harmony.
- Supports neurotypes including autistic, ADHD, SPD, and trauma-affected individuals.
- Sensitive emotional tone analysis, boundary negotiation, and interpersonal conflict guidance.
- Adaptive session memory tracks the last 5 user interactions for context-aware responses.
- Flexible integration for journaling, website, or web-based interfaces.

  * Alpha versions:
  On Poe:  https://poe.com/NeurodivergentCalm
On Facebook Messenger: https://m.me/1944934973012617?is_ai=1
    

**Lightweight CPU Version Notes:**

- Runs entirely on CPU (`device = "cpu"`) due to GPU limitations on Windows.
- Slower responses expected compared to GPU-based models.
- Developer has yet to test and troubleshoot all errors; project is open for feedback.

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
└─ README.md
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

## Hosting Alternatives and Past Attempts

- **Windows WSL2:** GPU passthrough not possible.  
- **VMware:** GPU passthrough unsupported on Windows host; Linux base OS required.  
- **Google Colab:** Works but static link required for iframe embedding; ngrok failed for persistent static link.  
- **Render / other cloud services:** Tested but unsuitable for GPU or static link needs.  
- **Replit:** GPU version works for development/testing; $200/year plan covers 1-year hosting.  
- **Cloudflare Tunnel + DuckDNS:** Recommended for self-hosted CPU version to provide sub-domain access.  

**Website Integration:**  
- Embedded via iframe at https://neurodivergentexperiences.com.  
- Paid version under development, includes feature-rich modules and token-based access.  
- Firebase + Stripe can handle user logins, payment splits, and webhook-based feature unlocks.  
- Discord bot integration possible (free and paid versions).

---

## Known Limitations

- CPU-only version is slower than GPU models.  
- Session memory limited to last 5 prompts.  
- Some Hugging Face models may require more RAM.  
- Developer has yet to test all edge cases; feedback welcome.  
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
