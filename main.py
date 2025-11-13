
# AI Connector Plus - Main Application
# FastAPI backend that integrates weather data with AI summaries


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from models.schemas import (
    TextRequest,
    CityRequest,
    WeatherResponse,
    SummaryResponse,
    WeatherSummaryResponse,
    HealthResponse
)
from services.weather_service import WeatherService
from services.ai_service import AIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
weather_service = WeatherService()
ai_service = AIService()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info(" Starting AI Connector Plus...")
    logger.info(" All services initialized")
    yield
    logger.info(" Shutting down AI Connector Plus...")
    await weather_service.close()
    await ai_service.close()

# Initialize FastAPI app
app = FastAPI(
    title="AI Connector Plus",
    description="A FastAPI backend that integrates weather data with AI-powered summaries",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (allows frontend apps to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (not secure for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all custom headers from frontend
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests"""
    logger.info(f" {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f" {request.method} {request.url.path} - Status: {response.status_code}")
    return response


# --------------------------------------------
# ENDPOINT 1: Health Check
# --------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    
    # Checks if the service is running
    
    # Returns:
    #     Service status and name
    
    logger.info("Health check requested")
    return {
        "status": "ok",
        "service": "AI Connector Plus"
    }


# ---------------------------------------------
# ENDPOINT 2: Get Weather
# -------------------------------------------
@app.get("/weather/{city}", response_model=WeatherResponse, tags=["Weather"])
async def get_weather(city: str):
    
    # Get current weather for a city
    
    # Args:
    #     city: Name of the city (e.g., "Riyadh", "London", "Tokyo")
    
    # Returns:
    #     Current temperature for the city
    
    # Example:
    #     GET /weather/Riyadh
    #     Returns: {"city": "Riyadh", "temperature": 32.1, "unit": "°C"}
    
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


# ----------------------------------------------
# ENDPOINT 3: AI Text Summarization
# ----------------------------------------------
@app.post("/summarize", response_model=SummaryResponse, tags=["AI"])
async def summarize_text(request: TextRequest):
    
    # Summarize text using AI
    
    # Args:
    #     request: JSON body with "text" field containing the text to summarize
    
    # Returns:
    #     AI-generated summary
    
    # Example:
    #     POST /summarize
    #     Body: {"text": "Long article about climate change..."}
    #     Returns: {"summary": "Climate change is accelerating..."}
    
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


# ---------------------------------------------
# ENDPOINT 4: Weather + AI Summary Combo
# ----------------------------------------------
@app.post("/weather-summary", response_model=WeatherSummaryResponse, tags=["Combined"])
async def get_weather_summary(request: CityRequest):
    
    # Get weather data and AI-generated friendly description
    
    # This endpoint combines two APIs:
    # 1. Fetches real weather data
    # 2. Asks AI to describe the weather in a friendly tone
    
    # Args:
    #     request: JSON body with "city" field
    
    # Returns:
    #     Weather data + AI-generated friendly description
    
    # Example:
    #     POST /weather-summary
    #     Body: {"city": "Jeddah"}
    #     Returns: {
    #         "city": "Jeddah",
    #         "temperature": 34.5,
    #         "summary": "It's a sunny day in Jeddah with warm temperatures..."
    #     }
    
    try:
        city = request.city
        logger.info(f"Generating weather summary for {city}")
        
        # Step 1: Getting weather data
        weather_data = await weather_service.get_weather(city)
        
        # Step 2: Creating prompt for AI
        prompt = f"""Describe today's weather in {city} where the temperature is {weather_data['temperature']}°C. 
        Write a short, friendly paragraph (2-3 sentences) that sounds natural and conversational. 
        Include suggestions for activities if appropriate."""
        
        # Step 3: Getting AI summary
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


#-------------------------------------------
# Root Endpoint (API Info)
#-------------------------------------------
@app.get("/", tags=["System"])
async def root():
    """
    API information and available endpoints
    """
    return {
        "message": "Welcome to AI Connector Plus :-)",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health - Check service status",
            "weather": "GET /weather/{city} - Get weather for a city",
            "summarize": "POST /summarize - Summarize text with AI",
            "weather_summary": "POST /weather-summary - Get weather + AI description",
            "docs": "GET /docs - Interactive API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  
        port=8000,
        reload=True,  # Auto-reloading on code changes (development only)
        log_level="info"
    )