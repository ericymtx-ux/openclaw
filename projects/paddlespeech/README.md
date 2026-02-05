# Whisper 语音转文字模块

**状态**: ✅ 已完成 (7/7 测试通过)

## 功能

- 将 Telegram 语音消息 (.ogg) 转为文字
- 支持 OpenAI Whisper 本地模型
- 自动格式转换 (OGG → WAV)

## 安装

```bash
# OpenAI Whisper (已通过 Homebrew 安装)
brew install whisper

# 或通过 pip
pip install openai-whisper

# ffmpeg (格式转换)
brew install ffmpeg
```

## 使用

```python
from voice_to_text import VoiceToText

processor = VoiceToText()

# 处理 Telegram 语音消息 (.ogg)
text = processor.process_ogg("/path/to/voice.ogg")
print(text)

# 或直接转录 WAV 文件
text = processor.transcribe("/path/to/audio.wav")
print(text)
```

## 便捷函数

```python
from voice_to_text import voice_to_text

# 一行代码完成转换
text = voice_to_text("/path/to/voice.ogg")
```

## 测试

```bash
python -m pytest test_voice_to_text.py -v
```

| 测试 | 状态 |
|------|------|
| test_init | ✅ |
| test_convert_ogg_to_wav | ✅ |
| test_transcribe | ✅ |
| test_process_ogg | ✅ |
| test_transcribe_file_not_found | ✅ |
| test_transcribe_error | ✅ |
| test_voice_to_text | ✅ |

## 文件结构

```
paddlespeech/
├── README.md
├── voice_to_text.py      # 主模块
└── test_voice_to_text.py # 测试用例
```

## 相关项目

- `voice-to-text/` - 完整语音处理 skill (支持 Whisper + PaddleSpeech)

---
*Tests verified: 2026-02-04*
