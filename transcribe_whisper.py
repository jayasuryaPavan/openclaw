#!/usr/bin/env python3
"""
Panda Chat — Whisper Transcription Helper

Transcribes an inbound audio file using OpenAI Whisper (local, tiny model).
Uses imageio-ffmpeg (bundled) for audio decoding — no system ffmpeg needed.

Usage:
    python transcribe_whisper.py <audio_file>
    python transcribe_whisper.py  (picks most recent file from inbound media dir)
"""

import os
import sys
import subprocess
import tempfile
import wave
import struct
import numpy as np


INBOUND_DIR = r"C:\Users\jayas\.openclaw\media\inbound"
AUDIO_EXTS = (".ogg", ".opus", ".mp3", ".wav", ".m4a", ".aac", ".webm", ".caf")


def get_ffmpeg():
    """Return the path to the bundled ffmpeg from imageio-ffmpeg."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise RuntimeError(
            "imageio-ffmpeg not found. Install it with: pip install imageio-ffmpeg"
        )


def decode_to_float_array(input_path):
    """
    Decode any audio format to a 16 kHz mono float32 numpy array.

    Strategy: use imageio-ffmpeg to convert to a raw PCM WAV, then read
    it with the stdlib `wave` module — this avoids Whisper's own ffmpeg
    subprocess (which requires system ffmpeg on PATH).
    """
    ffmpeg = get_ffmpeg()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cmd = [
            ffmpeg, "-y",
            "-i", input_path,
            "-ar", "16000",  # Whisper expects 16 kHz
            "-ac", "1",      # mono
            "-f", "wav",
            tmp_path,
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(
                "ffmpeg conversion failed:\n"
                + result.stderr.decode(errors="replace")[-400:]
            )

        with wave.open(tmp_path, "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            sampwidth = wf.getsampwidth()

        if sampwidth == 2:
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        elif sampwidth == 1:
            audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        else:
            audio = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0

        return audio
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def transcribe(file_path):
    """Transcribe an audio file to text using Whisper tiny model."""
    import whisper

    print(f"Transcribing: {file_path}", flush=True)
    audio = decode_to_float_array(file_path)

    # Load tiny model (fast, CPU-friendly)
    model = whisper.load_model("tiny")

    # Pass the audio array directly — no ffmpeg subprocess needed by Whisper
    result = whisper.transcribe(model, audio)
    return result["text"].strip()


def pick_inbound_file():
    """Return the most recently modified inbound audio file."""
    if not os.path.isdir(INBOUND_DIR):
        raise FileNotFoundError(f"Inbound media directory not found: {INBOUND_DIR}")
    files = [
        os.path.join(INBOUND_DIR, f)
        for f in os.listdir(INBOUND_DIR)
        if f.lower().endswith(AUDIO_EXTS)
    ]
    if not files:
        raise FileNotFoundError("No inbound audio files found.")
    return max(files, key=os.path.getmtime)


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else pick_inbound_file()

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        text = transcribe(file_path)
        print(text)
    except Exception as e:
        print(f"Transcription error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
