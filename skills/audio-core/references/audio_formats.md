# Audio Formats

Panda Chat Audio Core supports the following formats:

| Format | Extension(s) | Source | Notes |
|--------|-------------|--------|-------|
| **MP3** | `.mp3` | General | Standard compressed audio |
| **OGG/Opus** | `.ogg`, `.opus` | Telegram, WhatsApp | Native format for voice messages |
| **WAV** | `.wav` | General | Uncompressed, high quality |
| **M4A/AAC** | `.m4a`, `.aac` | iPhone, Android | Common mobile recording format |
| **CAF** | `.caf` | iOS/macOS | Core Audio Format, used by Voice Memos |
| **WebM** | `.webm` | Browser | Web-based audio recordings |

## Recommended Specs
- **Sample Rate**: 16kHz (STT) or 44.1kHz (high quality)
- **Channels**: Mono (preferred for speech-to-text)
- **Max File Size**: 25MB (Whisper API limit)

## Channel-Specific Formats
- **Telegram**: Sends voice notes as `.ogg` (Opus codec)
- **WhatsApp**: Sends voice as `.ogg` (Opus codec)
- **iMessage/BlueBubbles**: Sends voice as `.caf` or `.m4a`
- **Discord**: Sends voice as `.ogg` or `.webm`
