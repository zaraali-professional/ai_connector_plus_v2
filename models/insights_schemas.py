"""
Pydantic Models for AI Insights Layer
Defines request/response models for mood-based and activity-based insights
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Dict, Optional, List  # Add Optional and List
from datetime import datetime

class WeatherInsightRequest(BaseModel):
    """Request model for weather insight endpoint"""
    city: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Name of the city"
    )
    
    @field_validator('city')
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        """Validate and normalize city name"""
        if not v.strip():
            raise ValueError('City name cannot be empty')
        return v.strip().title()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"city": "Riyadh"},
                {"city": "Dubai"}
            ]
        }
    }


class MoodInsightRequest(BaseModel):
    """Request model for mood-based insight endpoint"""
    city: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Name of the city"
    )
    mood: Literal["happy", "tired", "stressed", "energetic", "relaxed", "sad", "excited"] = Field(
        ...,
        description="Current mood of the user"
    )
    
    @field_validator('city')
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        """Validate and normalize city name"""
        if not v.strip():
            raise ValueError('City name cannot be empty')
        return v.strip().title()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"city": "Cairo", "mood": "tired"},
                {"city": "Tokyo", "mood": "energetic"}
            ]
        }
    }


class ActivityInsightRequest(BaseModel):
    """Request model for activity-based insight endpoint"""
    city: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Name of the city"
    )
    activity_type: Literal["outdoor", "workout", "shopping", "dining", "sightseeing", "relaxing"] = Field(
        ...,
        description="Type of activity the user wants to do"
    )
    
    @field_validator('city')
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        """Validate and normalize city name"""
        if not v.strip():
            raise ValueError('City name cannot be empty')
        return v.strip().title()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"city": "Dubai", "activity_type": "outdoor"},
                {"city": "London", "activity_type": "sightseeing"}
            ]
        }
    }


class WeatherInsightResponse(BaseModel):
    """Response model for weather insight"""
    city: str = Field(..., description="City name")
    temperature: float = Field(..., description="Current temperature")
    unit: str = Field(default="°C", description="Temperature unit")
    insight: str = Field(..., description="AI-generated friendly weather insight with emojis")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "city": "Jeddah",
                    "temperature": 31.5,
                    "unit": "°C",
                    "insight": "It's a sunny afternoon in Jeddah ☀️ — perfect for a beach walk or an iced coffee!"
                }
            ]
        }
    }


class MoodInsightResponse(BaseModel):
    """Response model for mood-based insight"""
    city: str = Field(..., description="City name")
    temperature: float = Field(..., description="Current temperature")
    unit: str = Field(default="°C", description="Temperature unit")
    mood: str = Field(..., description="User's current mood")
    recommendation: str = Field(..., description="AI-generated personalized recommendation")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "city": "Cairo",
                    "temperature": 22.0,
                    "unit": "°C",
                    "mood": "tired",
                    "recommendation": "You're feeling tired and it's a cozy 22°C in Cairo 🌙 — maybe grab a warm drink and unwind indoors."
                }
            ]
        }
    }


class ActivityInsightResponse(BaseModel):
    """Response model for activity-based insight"""
    city: str = Field(..., description="City name")
    temperature: float = Field(..., description="Current temperature")
    unit: str = Field(default="°C", description="Temperature unit")
    activity_type: str = Field(..., description="Type of activity requested")
    suggestion: str = Field(..., description="AI-generated activity suggestion")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "city": "Riyadh",
                    "temperature": 38.5,
                    "unit": "°C",
                    "activity_type": "workout",
                    "suggestion": "It's quite warm in Riyadh 🏃 — try an early-morning jog instead of mid-day exercise."
                }
            ]
        }
    }
    
# Add these new models at the end of the file

class LanguageOption(str):
    """Supported languages"""
    EN = "en"  # English
    AR = "ar"  # Arabic
    ES = "es"  # Spanish
    FR = "fr"  # French
    DE = "de"  # German
    IT = "it"  # Italian
    JA = "ja"  # Japanese
    ZH = "zh-cn"  # Chinese (Simplified)


class WeatherInsightWithOptionsRequest(BaseModel):
    """Extended weather insight request with language and TTS options"""
    city: str = Field(..., min_length=2, max_length=50)
    lang: str = Field(default="en", description="Language code (en, ar, es, fr, etc.)")
    include_audio: bool = Field(default=False, description="Generate audio file")
    
    @field_validator('city')
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('City name cannot be empty')
        return v.strip().title()
    
    @field_validator('lang')
    @classmethod
    def lang_must_be_valid(cls, v: str) -> str:
        return v.lower().strip()


class MoodInsightWithOptionsRequest(BaseModel):
    """Extended mood insight request with language and TTS options"""
    city: str = Field(..., min_length=2, max_length=50)
    mood: Literal["happy", "tired", "stressed", "energetic", "relaxed", "sad", "excited"]
    lang: str = Field(default="en", description="Language code")
    include_audio: bool = Field(default=False, description="Generate audio file")
    
    @field_validator('city')
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('City name cannot be empty')
        return v.strip().title()
    
    @field_validator('lang')
    @classmethod
    def lang_must_be_valid(cls, v: str) -> str:
        return v.lower().strip()


class ActivityInsightWithOptionsRequest(BaseModel):
    """Extended activity insight request with language and TTS options"""
    city: str = Field(..., min_length=2, max_length=50)
    activity_type: Literal["outdoor", "workout", "shopping", "dining", "sightseeing", "relaxing"]
    lang: str = Field(default="en", description="Language code")
    include_audio: bool = Field(default=False, description="Generate audio file")
    
    @field_validator('city')
    @classmethod
    def city_must_be_valid(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('City name cannot be empty')
        return v.strip().title()
    
    @field_validator('lang')
    @classmethod
    def lang_must_be_valid(cls, v: str) -> str:
        return v.lower().strip()


class InsightWithAudioResponse(BaseModel):
    """Response with optional audio"""
    city: str
    temperature: float
    unit: str
    insight: str
    language: str
    audio_file: Optional[str] = Field(None, description="Path to audio file if generated")


class HistoryEntry(BaseModel):
    """Single history entry"""
    id: int
    timestamp: str
    type: str
    city: str
    data: Dict


class HistoryResponse(BaseModel):
    """Response for history endpoint"""
    total: int
    entries: List[HistoryEntry]