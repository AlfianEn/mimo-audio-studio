"""MiMo Audio Studio — Gradio web UI for Xiaomi MiMo audio AI toolkit."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

import mimo_client

load_dotenv()

# ── Helpers ──────────────────────────────────────────────────────────────────


def _save_temp(audio_bytes: bytes, ext: str = "mp3") -> str:
    """Write bytes to a temp file and return the path."""
    fd, path = tempfile.mkstemp(suffix=f".{ext}")
    os.write(fd, audio_bytes)
    os.close(fd)
    return path


def _check_key() -> str | None:
    if not mimo_client.API_KEY:
        return "⚠️ MIMO_API_KEY not set. Add it to .env or environment."
    return None


# ── Tab: TTS ─────────────────────────────────────────────────────────────────


def tab_tts(text: str, voice: str):
    err = _check_key()
    if err:
        return None, err
    if not text.strip():
        return None, "Masukkan teks yang ingin diubah ke suara."
    try:
        audio = mimo_client.tts(text, voice=voice)
        return _save_temp(audio), f"✅ Generated with voice '{voice}'"
    except Exception as e:
        return None, f"❌ {e}"


# ── Tab: Voice Clone ─────────────────────────────────────────────────────────


def tab_clone(text: str, audio_sample, voice_name: str):
    err = _check_key()
    if err:
        return None, err
    if not text.strip():
        return None, "Masukkan teks yang ingin diucapkan."
    if audio_sample is None:
        return None, "Upload sample audio untuk cloning."
    try:
        sample_path = audio_sample if isinstance(audio_sample, str) else audio_sample.name
        audio = mimo_client.voice_clone(text, sample_path, voice_name=voice_name)
        return _save_temp(audio), f"✅ Voice cloned from sample as '{voice_name}'"
    except Exception as e:
        return None, f"❌ {e}"


# ── Tab: Voice Design ────────────────────────────────────────────────────────


def tab_design(description: str, text: str):
    err = _check_key()
    if err:
        return None, err
    if not description.strip():
        return None, "Deskripsikan karakteristik suara yang diinginkan."
    if not text.strip():
        return None, "Masukkan teks yang ingin diucapkan."
    try:
        audio = mimo_client.voice_design(description, text)
        return _save_temp(audio), "✅ Custom voice generated"
    except Exception as e:
        return None, f"❌ {e}"


# ── Tab: Transcribe ──────────────────────────────────────────────────────────


def tab_transcribe(audio_file, lang: str):
    err = _check_key()
    if err:
        return None, err
    if audio_file is None:
        return None, "Upload audio file untuk ditranskripsi."
    try:
        path = audio_file if isinstance(audio_file, str) else audio_file.name
        text = mimo_client.transcribe(path, lang=lang)
        return text, "✅ Transcription complete"
    except Exception as e:
        return None, f"❌ {e}"


# ── Tab: Summarize ───────────────────────────────────────────────────────────


def tab_summarize(audio_file, lang: str):
    err = _check_key()
    if err:
        return None, None, err
    if audio_file is None:
        return None, None, "Upload audio file untuk di-summarize."
    try:
        path = audio_file if isinstance(audio_file, str) else audio_file.name
        result = mimo_client.summarize(path, lang=lang)
        return result["transcript"], result["summary"], "✅ Summarization complete"
    except Exception as e:
        return None, None, f"❌ {e}"


# ── UI ───────────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
.gradio-container { max-width: 900px !important; margin: auto !important; }
footer { display: none !important; }
"""


def build_app() -> gr.Blocks:
    with gr.Blocks(
        title="MiMo Audio Studio",
        
        
    ) as app:
        gr.Markdown(
            """
            # 🎙️ MiMo Audio Studio
            **Full audio AI toolkit powered by Xiaomi MiMo**
            Voice cloning · Voice design · TTS · Transcription · Summarization
            """
        )

        with gr.Tabs():
            # ── TTS Tab ──────────────────────────────────────────────────
            with gr.Tab("🔊 Text to Speech"):
                gr.Markdown("Ubah teks menjadi suara dengan berbagai pilihan voice MiMo.")
                with gr.Row():
                    tts_text = gr.Textbox(label="Teks", placeholder="Ketik teks di sini...", lines=4)
                    tts_voice = gr.Dropdown(
                        choices=mimo_client.DEFAULT_VOICES,
                        value="Mia",
                        label="Voice",
                    )
                tts_btn = gr.Button("🔊 Generate", variant="primary")
                tts_audio = gr.Audio(label="Output", type="filepath")
                tts_status = gr.Markdown()
                tts_btn.click(tab_tts, inputs=[tts_text, tts_voice], outputs=[tts_audio, tts_status])

            # ── Voice Clone Tab ──────────────────────────────────────────
            with gr.Tab("🎤 Voice Clone"):
                gr.Markdown("Upload sample suara, lalu MiMo akan meniru karakter suara tersebut.")
                clone_audio = gr.Audio(label="Sample Audio (upload)", type="filepath")
                clone_name = gr.Textbox(label="Voice Name", value="cloned", placeholder="Nama voice clone")
                clone_text = gr.Textbox(label="Teks yang diucapkan", placeholder="Apa yang ingin diucapkan?", lines=3)
                clone_btn = gr.Button("🎤 Clone & Speak", variant="primary")
                clone_output = gr.Audio(label="Output", type="filepath")
                clone_status = gr.Markdown()
                clone_btn.click(
                    tab_clone,
                    inputs=[clone_text, clone_audio, clone_name],
                    outputs=[clone_output, clone_status],
                )

            # ── Voice Design Tab ─────────────────────────────────────────
            with gr.Tab("🎨 Voice Design"):
                gr.Markdown("Buat suara custom dari deskripsi teks — tanpa sample audio.")
                design_desc = gr.Textbox(
                    label="Deskripsi Suara",
                    placeholder="Contoh: Suara wanita muda Indonesia, lembut dan hangat, cocok untuk narasi podcast",
                    lines=2,
                )
                design_text = gr.Textbox(label="Teks yang diucapkan", placeholder="Apa yang ingin diucapkan?", lines=3)
                design_btn = gr.Button("🎨 Design & Speak", variant="primary")
                design_audio = gr.Audio(label="Output", type="filepath")
                design_status = gr.Markdown()
                design_btn.click(tab_design, inputs=[design_desc, design_text], outputs=[design_audio, design_status])

            # ── Transcribe Tab ───────────────────────────────────────────
            with gr.Tab("📝 Transcribe"):
                gr.Markdown("Upload audio → dapatkan transkripsi teks lengkap.")
                tr_audio = gr.Audio(label="Upload Audio", type="filepath")
                tr_lang = gr.Dropdown(
                    choices=["Indonesian", "English", "Chinese", "Japanese", "Korean"],
                    value="Indonesian",
                    label="Bahasa",
                )
                tr_btn = gr.Button("📝 Transcribe", variant="primary")
                tr_output = gr.Textbox(label="Transkripsi", lines=10, interactive=False)
                tr_status = gr.Markdown()
                tr_btn.click(tab_transcribe, inputs=[tr_audio, tr_lang], outputs=[tr_output, tr_status])

            # ── Summarize Tab ────────────────────────────────────────────
            with gr.Tab("📋 Summarize"):
                gr.Markdown("Upload audio → transkripsi + ringkasan + poin-poin utama.")
                sum_audio = gr.Audio(label="Upload Audio", type="filepath")
                sum_lang = gr.Dropdown(
                    choices=["Indonesian", "English", "Chinese", "Japanese", "Korean"],
                    value="Indonesian",
                    label="Bahasa",
                )
                sum_btn = gr.Button("📋 Summarize", variant="primary")
                sum_transcript = gr.Textbox(label="Transkripsi", lines=8, interactive=False)
                sum_summary = gr.Markdown(label="Ringkasan")
                sum_status = gr.Markdown()
                sum_btn.click(
                    tab_summarize,
                    inputs=[sum_audio, sum_lang],
                    outputs=[sum_transcript, sum_summary, sum_status],
                )

        gr.Markdown(
            """
            ---
            *Powered by [Xiaomi MiMo](https://platform.xiaomimimo.com/) — STT · LLM · TTS · Voice Clone · Voice Design*
            """
        )

    return app


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft(), css=CUSTOM_CSS)
