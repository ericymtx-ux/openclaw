"""
语音转文字模块 - 使用 OpenAI Whisper
"""

import subprocess
import os
from pathlib import Path
from typing import Optional
import logging


class VoiceToText:
    """语音转文字处理器"""
    
    def __init__(self, model: str = "medium", output_dir: str = "/tmp/voice"):
        """
        初始化
        
        Args:
            model: Whisper 模型 (tiny, base, small, medium, large)
            output_dir: 临时文件目录
        """
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("VoiceToText")
    
    def _convert_ogg_to_wav(self, ogg_path: str) -> str:
        """将 OGG 转换为 WAV (16kHz, mono)"""
        stem = Path(ogg_path).stem  # 获取文件名不含扩展名
        wav_path = self.output_dir / f"{stem}.wav"
        
        subprocess.run([
            'ffmpeg', '-i', ogg_path,
            '-ar', '16000',  # 16kHz 采样率
            '-ac', '1',      # 单声道
            '-y',            # 覆盖已存在的文件
            str(wav_path)
        ], capture_output=True, check=True)
        
        return str(wav_path)
    
    def transcribe(self, audio_path: str, language: str = "zh") -> str:
        """
        语音转文字
        
        Args:
            audio_path: 音频文件路径 (.ogg, .wav, .mp3 等)
            language: 语言代码 (zh, en 等)
            
        Returns:
            识别的文字
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 转换 ogg 为 wav
        if audio_path.endswith('.ogg'):
            audio_path = self._convert_ogg_to_wav(audio_path)
        
        # 调用 whisper
        result = subprocess.run([
            'whisper', audio_path,
            '--model', self.model,
            '--language', language,
            '--output_format', 'txt',
            '--output_dir', str(self.output_dir),
            '--verbose', 'False'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            self.logger.error(f"Whisper 失败: {result.stderr}")
            raise RuntimeError(f"语音识别失败: {result.stderr}")
        
        # 读取结果
        txt_path = Path(audio_path).with_suffix(".txt")
        if txt_path.exists():
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        
        raise RuntimeError("未生成转录结果")
    
    def process_ogg(self, ogg_path: str, language: str = "zh") -> str:
        """
        处理 Telegram 语音消息 (.ogg)
        
        Args:
            ogg_path: OGG 文件路径
            language: 语言代码
            
        Returns:
            识别的文字
        """
        return self.transcribe(ogg_path, language)


# 便捷函数
def voice_to_text(ogg_path: str, language: str = "zh") -> str:
    """便捷转文字函数"""
    processor = VoiceToText()
    return processor.process_ogg(ogg_path, language)
