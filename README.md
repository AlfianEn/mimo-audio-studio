# MiMo Audio Studio

Full audio AI toolkit powered by [Xiaomi MiMo](https://platform.xiaomimimo.com/). Voice cloning, voice design, TTS, transcription, and summarization — all from one API key.

![MiMo Audio Studio](https://img.shields.io/badge/Powered%20by-Xiaomi%20MiMo-orange)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

| Feature | Model | Description |
|---------|-------|-------------|
| 🔊 **Text to Speech** | `mimo-v2.5-tts` | Generate natural speech from text with 9 built-in voices |
| 🎤 **Voice Clone** | `mimo-v2.5-tts-voiceclone` | Clone any voice from a short audio sample |
| 🎨 **Voice Design** | `mimo-v2.5-tts-voicedesign` | Create custom voices from text descriptions |
| 📝 **Transcribe** | `mimo-v2-omni` | Speech-to-text with multi-language support |
| 📋 **Summarize** | `mimo-v2-omni` + `mimo-v2.5-pro` | Audio → transcript → summary + key points |

## How it works

```
┌─────────────────────────────────────────────────────┐
│              MiMo Audio Studio                       │
│                                                      │
│  🔊 TTS ───────────→ mimo-v2.5-tts                  │
│  🎤 Voice Clone ───→ mimo-v2.5-tts-voiceclone       │
│  🎨 Voice Design ──→ mimo-v2.5-tts-voicedesign      │
│  📝 Transcribe ────→ mimo-v2-omni                   │
│  📋 Summarize ─────→ mimo-v2-omni + mimo-v2.5-pro   │
│                                                      │
│  All through ONE API key, ONE endpoint               │
└─────────────────────────────────────────────────────┘
```

## Quick start

### 1. Clone & install

Requires [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/AlfianEn/mimo-audio-studio.git
cd mimo-audio-studio
uv sync
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your MiMo API key
```

Get your API key from [Xiaomi MiMo Open Platform](https://platform.xiaomimimo.com/).

### 3. Run

```bash
uv run app.py
```

Open http://localhost:7860 in your browser.

## Available voices

| Voice | Style |
|-------|-------|
| **Mia** | Natural, warm — best for Indonesian |
| **Chloe** | Clear, professional |
| **Milo** | Male, friendly |
| **Dean** | Male, deep |
| **mimo_default** | Default MiMo voice |
| **冰糖** | Chinese, sweet |
| **茉莉** | Chinese, gentle |
| **苏打** | Chinese, energetic |
| **白桦** | Chinese, calm |

## Project structure

```
mimo-audio-studio/
├── app.py            # Gradio web UI (5 tabs)
├── mimo_client.py    # MiMo API client (TTS, STT, clone, design, summarize)
├── pyproject.toml    # Project config & dependencies
├── .env.example      # Environment template
└── LICENSE           # MIT
```

## API usage (without Gradio)

```python
import mimo_client

# Text to speech
audio = mimo_client.tts("Halo, apa kabar?", voice="Mia")

# Voice clone
audio = mimo_client.voice_clone("Halo dari voice clone!", "sample.mp3")

# Voice design
audio = mimo_client.voice_design("Suara pria dewasa, tegas dan hangat", "Selamat pagi")

# Transcription
text = mimo_client.transcribe("recording.mp3")

# Summarize
result = mimo_client.summarize("meeting.mp3")
print(result["transcript"])
print(result["summary"])
```

## Why this exists

Most audio AI tools focus on a single capability — either TTS, or transcription, or cloning. MiMo Audio Studio brings all of Xiaomi MiMo's audio capabilities into one unified toolkit:

- **Voice cloning** that works from a single sample — no training, no GPU
- **Voice design** from text descriptions — create voices that don't exist
- **Full pipeline** — STT → reasoning → TTS, all from one API key
- **Indonesian-native** — optimized for Bahasa Indonesia with multi-language support

Built as a showcase for the [MiMo 100T Program](https://platform.xiaomimimo.com/).

## Stack

- Python 3.11+
- [Gradio](https://gradio.app/) — web UI
- [httpx](https://github.com/encode/httpx) — HTTP client
- [Xiaomi MiMo](https://platform.xiaomimimo.com/) — all AI models

## License

MIT
