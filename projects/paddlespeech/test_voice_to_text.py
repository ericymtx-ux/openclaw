"""
语音转文字测试用例
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from subprocess import CompletedProcess

from voice_to_text import VoiceToText, voice_to_text


class TestVoiceToText:
    """语音转文字测试"""
    
    def test_init(self):
        """测试初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = VoiceToText(model="base", output_dir=tmpdir)
            assert processor.model == "base"
            assert processor.output_dir == Path(tmpdir)
    
    def test_convert_ogg_to_wav(self):
        """测试 OGG 转 WAV"""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = VoiceToText(output_dir=tmpdir)
            
            # 创建假 OGG 文件
            ogg_path = Path(tmpdir) / "test.ogg"
            ogg_path.write_bytes(b'fake ogg data')
            
            # Mock ffmpeg
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = CompletedProcess(args=[], returncode=0)
                
                wav_path = processor._convert_ogg_to_wav(str(ogg_path))
                
                assert wav_path.endswith('.wav')
                assert 'ffmpeg' in str(mock_run.call_args)
    
    @patch('subprocess.run')
    def test_transcribe(self, mock_run):
        """测试转文字"""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = VoiceToText(output_dir=tmpdir)
            
            # 创建假 WAV 文件
            wav_path = Path(tmpdir) / "test.wav"
            wav_path.write_bytes(b'fake wav data')
            
            # 创建假输出文件
            txt_path = Path(tmpdir) / "test.txt"
            txt_path.write_text("测试转录结果")
            
            # Mock whisper
            mock_run.return_value = CompletedProcess(args=[], returncode=0)
            
            result = processor.transcribe(str(wav_path))
            
            assert result == "测试转录结果"
    
    @patch('subprocess.run')
    def test_process_ogg(self, mock_run):
        """测试处理 OGG 文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = VoiceToText(output_dir=tmpdir)
            
            # 创建假 OGG 文件和输出
            ogg_path = Path(tmpdir) / "test.ogg"
            ogg_path.write_bytes(b'fake ogg data')
            
            wav_path = Path(tmpdir) / "test.wav"
            wav_path.write_bytes(b'fake wav data')
            
            txt_path = Path(tmpdir) / "test.txt"
            txt_path.write_text("OGG 转录结果")
            
            mock_run.return_value = CompletedProcess(args=[], returncode=0)
            
            result = processor.process_ogg(str(ogg_path))
            
            assert result == "OGG 转录结果"
    
    def test_transcribe_file_not_found(self):
        """测试文件不存在"""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = VoiceToText(output_dir=tmpdir)
            
            with pytest.raises(FileNotFoundError):
                processor.transcribe(str(Path(tmpdir) / "nonexistent.wav"))
    
    @patch('subprocess.run')
    def test_transcribe_error(self, mock_run):
        """测试转录错误"""
        with tempfile.TemporaryDirectory() as tmpdir:
            processor = VoiceToText(output_dir=tmpdir)
            
            wav_path = Path(tmpdir) / "test.wav"
            wav_path.write_bytes(b'fake wav data')
            
            mock_run.return_value = CompletedProcess(
                args=[], 
                returncode=1, 
                stderr="Error: model not found"
            )
            
            with pytest.raises(RuntimeError):
                processor.transcribe(str(wav_path))


class TestVoiceToTextConvenience:
    """便捷函数测试"""
    
    @patch('voice_to_text.VoiceToText.process_ogg')
    def test_voice_to_text(self, mock_process):
        """测试便捷函数"""
        mock_process.return_value = "测试结果"
        
        result = voice_to_text("/path/to/test.ogg")
        
        assert result == "测试结果"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
