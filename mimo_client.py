"""MiMo API client — covers TTS, voice cloning, voice design, STT, and reasoning."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("MIMO_BASE_URL", "https://token-plan-sgp.xiaomimimo.com/v1")
API_KEY = os.getenv("MIMO_API_KEY", "")

DEFAULT_VOICES = ["Mia", "Chloe", "Milo", "Dean", "mimo_default", "冰糖", "茉莉", "苏打", "白桦"]

_timeout = httpx.Timeout(120.0, connect=10.0)


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


# ── TTS ──────────────────────────────────────────────────────────────────────


def tts(text: str, voice: str = "Mia", fmt: str = "mp3") -> bytes:
    """Generate speech from text using a default voice."""
    payload = {
        "model": "mimo-v2.5-tts",
        "messages": [
            {"role": "user", "content": ""},
            {"role": "assistant", "content": text},
        ],
        "modalities": ["text", "audio"],
        "audio": {"voice": voice, "format": fmt},
    }
    with httpx.Client(timeout=_timeout) as c:
        resp = c.post(f"{BASE_URL}/chat/completions", headers=_headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()
    audio_b64 = data["choices"][0]["message"]["audio"]["data"]
    return base64.b64decode(audio_b64)


# ── Voice Clone ──────────────────────────────────────────────────────────────


def voice_clone(
    text: str,
    audio_path: str,
    voice_name: str = "cloned",
    fmt: str = "mp3",
) -> bytes:
    """Clone a voice from an audio sample and speak the given text."""
    audio_bytes = Path(audio_path).read_bytes()
    audio_b64 = base64.b64encode(audio_bytes).decode()

    payload = {
        "model": "mimo-v2.5-tts-voiceclone",
        "messages": [
            {"role": "user", "content": ""},
            {"role": "assistant", "content": text},
        ],
        "modalities": ["text", "audio"],
        "audio": {"voice": voice_name, "format": fmt},
        "extra": {"voice_clone_audio": audio_b64},
    }
    with httpx.Client(timeout=_timeout) as c:
        resp = c.post(f"{BASE_URL}/chat/completions", headers=_headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()
    audio_b64_out = data["choices"][0]["message"]["audio"]["data"]
    return base64.b64decode(audio_b64_out)


# ── Voice Design ─────────────────────────────────────────────────────────────


def voice_design(description: str, text: str, fmt: str = "mp3") -> bytes:
    """Create a custom voice from a text description, then speak."""
    payload = {
        "model": "mimo-v2.5-tts-voicedesign",
        "messages": [
            {"role": "user", "content": description},
            {"role": "assistant", "content": text},
        ],
        "modalities": ["text", "audio"],
        "audio": {"voice": "mimo_default", "format": fmt},
    }
    with httpx.Client(timeout=_timeout) as c:
        resp = c.post(f"{BASE_URL}/chat/completions", headers=_headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()
    audio_b64 = data["choices"][0]["message"]["audio"]["data"]
    return base64.b64decode(audio_b64)


# ── STT (Speech-to-Text) ────────────────────────────────────────────────────


def transcribe(audio_path: str, lang: str = "Indonesian") -> str:
    """Transcribe audio to text using mimo-v2-omni."""
    audio_bytes = Path(audio_path).read_bytes()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    ext = Path(audio_path).suffix.lower().lstrip(".")
    audio_fmt = {"ogg": "ogg", "oga": "ogg", "mp3": "mp3", "wav": "wav", "m4a": "mp3"}.get(ext, "ogg")

    payload = {
        "model": "mimo-v2-omni",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Transkripsikan audio ini ke teks Bahasa {lang}. Hanya keluarkan teks hasil transkripsi, tanpa penjelasan.",
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {"data": audio_b64, "format": audio_fmt},
                    },
                ],
            }
        ],
        "max_tokens": 4096,
    }
    with httpx.Client(timeout=_timeout) as c:
        resp = c.post(f"{BASE_URL}/chat/completions", headers=_headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"]


# ── Summarize ────────────────────────────────────────────────────────────────


def summarize(audio_path: str, lang: str = "Indonesian") -> dict[str, str]:
    """Transcribe audio, then summarize and extract key points via reasoning."""
    transcript = transcribe(audio_path, lang)

    prompt = (
        f"Kamu adalah asisten analisis audio. Berikut transkripsi rekaman audio:\n\n"
        f"---\n{transcript}\n---\n\n"
        f"Buatlah:\n"
        f"1. **Ringkasan** (3-5 kalimat)\n"
        f"2. **Poin-poin utama** (bullet points)\n"
        f"3. **Kesimpulan** (1-2 kalimat)\n\n"
        f"Jawab dalam Bahasa {lang}. Gunakan format markdown."
    )
    payload = {
        "model": "mimo-v2.5-pro",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "temperature": 0.3,
    }
    with httpx.Client(timeout=_timeout) as c:
        resp = c.post(f"{BASE_URL}/chat/completions", headers=_headers(), json=payload)
        resp.raise_for_status()
        data = resp.json()

    summary = data["choices"][0]["message"]["content"]
    return {"transcript": transcript, "summary": summary}
