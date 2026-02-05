#!/usr/bin/env python3
"""
语音转文字脚本 - 支持 Telegram 语音消息

用法:
    python voice_to_text.py <audio_file>
    python voice_to_text.py --file /path/to/audio.ogg
    python voice_to_text.py --url "https://..."

依赖:
    - whisper (openai-whisper): brew install openai-whisper
    - ffmpeg: brew install ffmpeg
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def convert_to_wav(input_path: str, output_path: str = None) -> str:
    """将音频转换为 16kHz WAV 格式"""
    if output_path is None:
        output_path = input_path.replace(
            Path(input_path).suffix, '.wav'
        )
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-ar', '16000',
        '-ac', '1',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"音频转换失败: {result.stderr}")
    
    return output_path


def transcribe_whisper(audio_path: str, language: str = 'zh', 
                       model: str = 'small', verbose: bool = False) -> str:
    """使用 Whisper 进行语音识别"""
    cmd = [
        'whisper',
        audio_path,
        '--model', model,
        '--language', language,
        '--output_format', 'txt',
        '--output_dir', tempfile.gettempdir()
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Whisper 识别失败: {result.stderr}")
    
    # 读取生成的 txt 文件
    txt_path = os.path.join(
        tempfile.gettempdir(),
        Path(audio_path).stem + '.txt'
    )
    
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        return text
    
    raise RuntimeError("未能获取识别结果")


def voice_to_text(input_path: str, language: str = 'zh',
                  use_whisper: bool = True, verbose: bool = False) -> str:
    """
    主函数: 将语音转换为文字
    
    Args:
        input_path: 输入音频文件路径
        language: 语言代码 ('zh' for Chinese)
        use_whisper: 是否使用 Whisper (否则尝试 PaddleSpeech)
        verbose: 是否输出详细信息
    
    Returns:
        识别出的文字
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"音频文件不存在: {input_path}")
    
    ext = Path(input_path).suffix.lower()
    
    # 如果是 ogg (Telegram 语音格式)，先转换为 wav
    if ext == '.ogg':
        wav_path = convert_to_wav(input_path)
    elif ext in ['.m4a', '.mp3', '.wav', '.mp4']:
        wav_path = input_path
    else:
        # 其他格式也转换为 wav
        wav_path = convert_to_wav(input_path)
    
    try:
        if use_whisper:
            result = transcribe_whisper(wav_path, language, verbose=verbose)
        else:
            # 备用: PaddleSpeech (如果可用)
            result = transcribe_paddlespeech(wav_path, language)
        
        if verbose:
            print(f"✓ 识别成功: {result}")
        
        return result
    
    except Exception as e:
        raise RuntimeError(f"语音识别失败: {e}")


def transcribe_paddlespeech(audio_path: str, language: str) -> str:
    """PaddleSpeech 备用方案"""
    try:
        from paddlespeech.cli.whisper.infer import WhisperExecutor
        
        whisper = WhisperExecutor()
        result = whisper(audio_file=audio_path, lang=language)
        return result
    except ImportError:
        raise RuntimeError("PaddleSpeech 不可用，请使用 Whisper")


def main():
    parser = argparse.ArgumentParser(
        description='语音转文字工具 (支持 Telegram 语音消息)'
    )
    parser.add_argument('input', nargs='?', help='输入音频文件路径')
    parser.add_argument('--file', '-f', help='输入音频文件路径')
    parser.add_argument('--language', '-l', default='zh',
                        help='语言代码 (默认: zh)')
    parser.add_argument('--model', '-m', default='small',
                        help='Whisper 模型: tiny, base, small, medium, large')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='输出详细信息')
    parser.add_argument('--paddlespeech', action='store_true',
                        help='使用 PaddleSpeech (而不是 Whisper)')
    
    args = parser.parse_args()
    
    # 获取输入文件
    input_path = args.file or args.input
    
    if not input_path:
        parser.print_help()
        sys.exit(1)
    
    try:
        result = voice_to_text(
            input_path,
            language=args.language,
            use_whisper=not args.paddlespeech,
            verbose=args.verbose
        )
        print(result)
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
