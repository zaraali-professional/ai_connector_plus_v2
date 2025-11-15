"""
Text-to-Speech Service - Converts text to audio
Uses Google TTS (gTTS) for generating speech
"""

import logging
import os
from pathlib import Path
from gtts import gTTS
import hashlib
from datetime import datetime
from typing import Dict  # Add this import

logger = logging.getLogger(__name__)


class TTSService:
    """
    Service for converting text to speech
    Supports multiple languages via gTTS
    """
    
    def __init__(self, audio_dir: str = "audio_files"):
        """
        Initialize TTS service
        
        Args:
            audio_dir: Directory to store generated audio files
        """
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(exist_ok=True)
        logger.info(f"🔊 TTS Service initialized (audio dir: {audio_dir})")
    
    def _generate_filename(self, text: str, lang: str) -> str:
        """
        Generate unique filename based on text hash
        
        Args:
            text: Text content
            lang: Language code
        
        Returns:
            Filename for the audio file
        """
        # Create hash of text + language
        content = f"{text}_{lang}"
        hash_object = hashlib.md5(content.encode())
        hash_hex = hash_object.hexdigest()
        return f"tts_{hash_hex}.mp3"
    
    def text_to_speech(self, text: str, lang: str = "en") -> str:
        """
        Convert text to speech and save as MP3
        
        Args:
            text: Text to convert
            lang: Language code (en, ar, es, fr, etc.)
        
        Returns:
            Generated audio filename (without directory)
        """
        try:
            # Clean text (remove emojis for better TTS)
            clean_text = self._clean_text_for_tts(text)
            
            # Generate filename
            filename = self._generate_filename(clean_text, lang)
            file_path = self.audio_dir / filename
            
            # Check if file already exists (cache)
            if file_path.exists():
                logger.info(f"🎵 Using cached audio: {filename}")
                return filename
            
            # Generate speech
            logger.info(f"🎙️ Generating speech for text (lang: {lang})")
            tts = gTTS(text=clean_text, lang=lang, slow=False)
            tts.save(str(file_path))
            
            logger.info(f"☑️ Audio generated: {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"❌ Error generating speech: {e}")
            raise ValueError(f"Failed to generate speech: {str(e)}")
    
    def _clean_text_for_tts(self, text: str) -> str:
        """
        Clean text for better TTS output
        Removes or replaces emojis and special characters
        
        Args:
            text: Original text
        
        Returns:
            Cleaned text
        """
        import re  # Move import to top of file for better practice
        
        # Common emoji replacements for better speech
        replacements = {
            "☀️": "sunny",
            "🌤️": "partly sunny",
            "☁️": "cloudy",
            "🌧️": "rainy",
            "❄️": "snowy",
            "🌙": "",
            "☕": "",
            "🏃": "",
            "🛍️": "",
            "🍽️": "",
            "📸": "",
            "🧘": "",
            "💪": "",
            "🎉": "",
            "🌻": "",
            "🌿": "",
            "°C": "degrees Celsius",
            "°F": "degrees Fahrenheit"
        }
        
        cleaned = text
        for emoji, replacement in replacements.items():
            cleaned = cleaned.replace(emoji, replacement)
        
        # Remove any remaining emojis (basic approach)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            "]+", flags=re.UNICODE)
        cleaned = emoji_pattern.sub('', cleaned)
        
        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def get_audio_info(self, file_path: str) -> Dict:
        """
        Get information about an audio file
        
        Args:
            file_path: Path to audio file
        
        Returns:
            Dictionary with file info
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}
        
        stat = path.stat()
        return {
            "filename": path.name,
            "size_bytes": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 2),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
        }