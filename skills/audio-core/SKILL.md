---
name: audio-core
description: Audio processing capabilities for Panda Chat. Use when you need to transcribe voice messages (STT), validate audio files, or generate expressive speech output (TTS).
---

# Audio Core

## Overview

The Audio Core skill enables Panda Chat to interact through sound. It handles the conversion between text and speech, allowing for voice-first interactions.

## Capabilities

### 1. Speech-to-Text (STT)
Converts incoming voice messages or audio files into text using models like OpenAI Whisper.
- **Trigger**: Incoming audio/voice message.
- **Tool**: `scripts/transcribe.py`.

### 2. Audio Validation
Checks audio files for transcription readiness (format, size, integrity).
- **Tool**: `scripts/voice_check.py`.

### 3. Text-to-Speech (TTS)
Generates natural-sounding speech from text using the built-in `tts` tool (Edge TTS provider).
- **Trigger**: User requests voice response or `/tts` command.

## Workflow

1. **Validation**: When an audio message is received, use `scripts/voice_check.py` to verify format and quality.
2. **Transcription**: Use `scripts/transcribe.py` to get the text from the audio.
3. **Analysis**: Pass transcribed text to `nlp-core` for intent/sentiment analysis.
4. **Response**: If audio response is needed, use the built-in `tts` tool.

## Resources

### scripts/
- `transcribe.py`: Audio-to-text transcription with format validation and structured output.
- `voice_check.py`: Validates audio files for transcription readiness (format, size, header integrity).

### references/
- `audio_formats.md`: Supported audio formats, specs, and channel-specific format mapping.

