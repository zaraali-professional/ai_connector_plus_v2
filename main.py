"""
AI Connector Plus - Main Application
FastAPI backend that integrates weather data with AI summaries
Version 3.0.0 - With Voice Generation, History Tracking, and Multilingual Support
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import logging
from contextlib import asynccontextmanager
from typing import Optional

from models.schemas import (
    TextRequest,
    CityRequest,
    WeatherResponse,
    SummaryResponse,
    WeatherSummaryResponse,
    HealthResponse
)
from models.insights_schemas import (
    WeatherInsightRequest,
    MoodInsightRequest,
    ActivityInsightRequest,
    WeatherInsightResponse,
    MoodInsightResponse,
    ActivityInsightResponse,
    WeatherInsightWithOptionsRequest,
    MoodInsightWithOptionsRequest,
    ActivityInsightWithOptionsRequest,
    HistoryResponse
)
from services.weather_service import WeatherService
from services.ai_service import AIService
from services.ai_insights_service import AIInsightsService
from services.history_manager import HistoryManager
from services.tts_service import TTSService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
weather_service = WeatherService()
ai_service = AIService()
insights_service = AIInsightsService(weather_service, ai_service)
history_manager = HistoryManager()
tts_service = TTSService()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("🚀 Starting AI Connector Plus v3.0...")
    logger.info("✅ All services initialized")
    logger.info("🆕 New Features: Voice Generation, History Tracking, Multilingual Support")
    yield
    logger.info("👋 Shutting down AI Connector Plus...")
    await weather_service.close()
    await ai_service.close()

# Initialize FastAPI app
app = FastAPI(
    title="AI Connector Plus",
    description="A FastAPI backend with weather data, AI insights, voice generation, history tracking, and multilingual support",
    version="3.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests"""
    logger.info(f"📥 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code}")
    return response


# ============================================
# ENDPOINT 1: Health Check
# ============================================
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check if the service is running"""
    logger.info("Health check requested")
    return {
        "status": "ok",
        "service": "AI Connector Plus v3.0"
    }


# ============================================
# ENDPOINT 2: Get Weather
# ============================================
@app.get("/weather/{city}", response_model=WeatherResponse, tags=["Weather"])
async def get_weather(city: str):
    """Get current weather for a city"""
    try:
        logger.info(f"Fetching weather for {city}")
        weather_data = await weather_service.get_weather(city)
        logger.info(f"Weather for {city}: {weather_data['temperature']}°C")
        return weather_data
    except ValueError as e:
        logger.error(f"City not found: {city}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching weather: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")


# ============================================
# ENDPOINT 3: AI Text Summarization
# ============================================
@app.post("/summarize", response_model=SummaryResponse, tags=["AI"])
async def summarize_text(request: TextRequest):
    """Summarize text using AI"""
    try:
        logger.info(f"Summarizing text (length: {len(request.text)} chars)")
        
        if len(request.text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Text too short. Please provide at least 50 characters."
            )
        
        summary = await ai_service.summarize_text(request.text)
        logger.info(f"Summary generated (length: {len(summary)} chars)")
        return {"summary": summary}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")


# ============================================
# ENDPOINT 4: Weather + AI Summary Combo
# ============================================
@app.post("/weather-summary", response_model=WeatherSummaryResponse, tags=["Combined"])
async def get_weather_summary(request: CityRequest):
    """Get weather data and AI-generated friendly description"""
    try:
        city = request.city
        logger.info(f"Generating weather summary for {city}")
        
        weather_data = await weather_service.get_weather(city)
        
        prompt = f"""Describe today's weather in {city} where the temperature is {weather_data['temperature']}°C. 
        Write a short, friendly paragraph (2-3 sentences) that sounds natural and conversational. 
        Include suggestions for activities if appropriate."""
        
        summary = await ai_service.summarize_text(prompt)
        
        logger.info(f"Weather summary generated for {city}")
        
        return {
            "city": weather_data["city"],
            "temperature": weather_data["temperature"],
            "unit": weather_data["unit"],
            "summary": summary
        }
    
    except ValueError as e:
        logger.error(f"City not found: {city}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating weather summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate weather summary")


# ============================================
# AI INSIGHTS LAYER - BASIC ENDPOINTS
# ============================================

@app.post("/insight/weather", response_model=WeatherInsightResponse, tags=["AI Insights"])
async def get_weather_insight(request: WeatherInsightRequest):
    """Get AI-generated friendly weather insight with emojis"""
    try:
        logger.info(f"Weather insight requested for {request.city}")
        result = await insights_service.get_weather_insight(request.city)
        
        # Add to history
        history_manager.add_entry("weather", request.city, result)
        
        return result
    except ValueError as e:
        logger.error(f"City not found: {request.city}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating weather insight: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate weather insight")


@app.post("/insight/mood", response_model=MoodInsightResponse, tags=["AI Insights"])
async def get_mood_insight(request: MoodInsightRequest):
    """Get mood-based personalized recommendations"""
    try:
        logger.info(f"Mood insight requested for {request.city} (mood: {request.mood})")
        result = await insights_service.get_mood_insight(request.city, request.mood)
        
        # Add to history
        history_manager.add_entry("mood", request.city, result)
        
        return result
    except ValueError as e:
        logger.error(f"City not found: {request.city}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating mood insight: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate mood insight")


@app.post("/insight/activity", response_model=ActivityInsightResponse, tags=["AI Insights"])
async def get_activity_insight(request: ActivityInsightRequest):
    """Get activity-specific smart suggestions"""
    try:
        logger.info(f"Activity insight requested for {request.city} (activity: {request.activity_type})")
        result = await insights_service.get_activity_insight(request.city, request.activity_type)
        
        # Add to history
        history_manager.add_entry("activity", request.city, result)
        
        return result
    except ValueError as e:
        logger.error(f"City not found: {request.city}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating activity insight: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate activity insight")


# ============================================
# BONUS FEATURE 1: VOICE GENERATION (TTS)
# ============================================

@app.post("/insight/weather/v2", tags=["AI Insights - Enhanced"])
async def get_weather_insight_v2(request: WeatherInsightWithOptionsRequest):
    """
    Enhanced weather insight with multilingual and voice support
    
    Parameters:
    - city: City name
    - lang: Language code (en, ar, es, fr, de, it, ja, zh-cn)
    - include_audio: Generate audio file (true/false)
    
    Example:
        {"city": "Riyadh", "lang": "ar", "include_audio": true}
    """
    try:
        logger.info(f"Enhanced weather insight: {request.city} (lang: {request.lang}, audio: {request.include_audio})")
        
        result = await insights_service.get_weather_insight_with_options(
            city=request.city,
            lang=request.lang,
            include_audio=request.include_audio,
            tts_service=tts_service if request.include_audio else None
        )
        
        # Add to history
        history_manager.add_entry("weather_v2", request.city, result)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}", tags=["Voice Generation"])
async def get_audio_file(filename: str):
    """
    Download generated audio file
    
    Parameters:
    - filename: Name of the audio file (from insight response)
    """
    try:
        file_path = f"audio_files/{filename}"
        import os
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error retrieving audio: {e}")
        raise HTTPException(status_code=404, detail="Audio file not found")


# ============================================
# BONUS FEATURE 2: HISTORY TRACKING
# ============================================

@app.get("/insight/history", response_model=HistoryResponse, tags=["History"])
async def get_insight_history(limit: Optional[int] = 10):
    """
    Get history of generated insights
    
    Parameters:
    - limit: Maximum number of entries to return (default: 10)
    
    Returns last N insights with timestamps
    """
    try:
        logger.info(f"History requested (limit: {limit})")
        entries = history_manager.get_history(limit=limit)
        
        return {
            "total": len(entries),
            "entries": entries
        }
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@app.get("/insight/history/stats", tags=["History"])
async def get_history_stats():
    """Get statistics about insight history"""
    try:
        stats = history_manager.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")


@app.delete("/insight/history", tags=["History"])
async def clear_history():
    """Clear all insight history"""
    try:
        history_manager.clear_history()
        return {"message": "History cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history")


# ============================================
# BONUS FEATURE 3: MULTILINGUAL SUPPORT INFO
# ============================================

@app.get("/languages", tags=["System"])
async def get_supported_languages():
    """
    Get list of supported languages
    
    Returns language codes and names
    """
    return {
        "supported_languages": {
            "en": "English",
            "ar": "Arabic (العربية)",
            "es": "Spanish (Español)",
            "fr": "French (Français)",
            "de": "German (Deutsch)",
            "it": "Italian (Italiano)",
            "ja": "Japanese (日本語)",
            "zh-cn": "Chinese Simplified (简体中文)"
        },
        "usage": "Add 'lang' parameter to any insight request",
        "example": {
            "city": "Riyadh",
            "lang": "ar",
            "include_audio": True
        }
    }


# ============================================
# Root Endpoint (API Info)
# ============================================
@app.get("/", tags=["System"])
async def root():
    """API information and available endpoints"""
    return {
        "message": "Welcome to AI Connector Plus! 🚀",
        "version": "3.0.0",
        "features": {
            "core": "Weather data + AI insights",
            "voice": "Text-to-Speech generation",
            "history": "Last 10 insights tracking",
            "multilingual": "8 languages supported"
        },
        "endpoints": {
            "health": "GET /health - Check service status",
            "weather": "GET /weather/{city} - Get weather",
            "summarize": "POST /summarize - Summarize text",
            "weather_summary": "POST /weather-summary - Weather + AI",
            "insight_weather": "POST /insight/weather - Weather insights",
            "insight_mood": "POST /insight/mood - Mood-based recommendations",
            "insight_activity": "POST /insight/activity - Activity suggestions",
            "insight_weather_v2": "POST /insight/weather/v2 - Enhanced with voice & multilingual",
            "history": "GET /insight/history - View insight history",
            "history_stats": "GET /insight/history/stats - History statistics",
            "languages": "GET /languages - Supported languages",
            "audio": "GET /audio/{filename} - Download audio file",
            "docs": "GET /docs - Interactive API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )