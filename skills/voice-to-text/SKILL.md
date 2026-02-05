---
name: voice-to-text
description: Local speech-to-text with OpenAI Whisper and PaddleSpeech. Supports Chinese voice messages from Telegram.
homepage: https://github.com/openclaw/openclaw/tree/main/projects/voice-to-text
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "requires": 
          {
            "bins": ["whisper", "ffmpeg"],
            "python": ">=3.11"
          },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "openai-whisper",
              "bins": ["whisper"],
              "label": "Install OpenAI Whisper (brew)"
            },
            {
              "id": "ffmpeg",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install FFmpeg (brew)"
            },
            {
              "id": "pip",
              "kind": "pip",
              "package": "voice-to-text",
              "path": "projects/voice-to-text",
              "label": "Install voice-to-text package"
            }
          ],
        "skills": ["whisper"],
      },
  }
---

# Voice-to-Text Skill

Use `voice-to-text` to transcribe audio files locally. Supports Chinese speech recognition for Telegram voice messages.

## Quick Start

### Python API

```python
from src.voice_to_text import transcribe

# Transcribe Telegram voice message
text = transcribe("/path/to/voice.ogg", language="zh")
print(text)
```

### CLI

```bash
# Transcribe audio file
voice-to-text --file voice.ogg --language zh

# With verbose output
voice-to-text --file voice.ogg --verbose
```

## Features

- 🎙️ **OpenAI Whisper** - Local transcription, privacy-first
- 🇨🇳 **Chinese Support** - Native Mandarin recognition
- 📱 **Telegram Ready** - Handles .ogg voice messages
- ⚡ **Fast** - < 5 seconds response time
- 🔄 **Fallback** - PaddleSpeech if Whisper unavailable

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_CACHE_DIR` | `~/.cache/whisper` | Model cache directory |
| `WHISPER_MODEL` | `small` | Model size (tiny/base/small/medium/large) |

### Model Selection

```python
from src.voice_to_text import VoiceToText

# Faster, smaller model
whisper = VoiceToText(engine="whisper", model="tiny")

# More accurate, larger model
whisper = VoiceToText(engine="whisper", model="medium")
```

## Requirements

- macOS with Homebrew
- Python 3.11+
- OpenAI Whisper (`brew install openai-whisper`)
- FFmpeg (`brew install ffmpeg`)

## Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Notes

- Whisper models are cached in `~/.cache/whisper`
- First run downloads model (~244MB for small model)
- CPU inference, no GPU required
- Telegram voice messages are .ogg format, automatically converted
