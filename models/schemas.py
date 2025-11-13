
# Pydantic Models for Request/Response Validation
# These define the "shape" of data that flows through the API


from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "ok",
                    "service": "AI Connector Plus"
                }
            ]
        }
    }


class TextRequest(BaseModel):
    """Request model for text summarization"""
    text: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Text to summarize (50-10000 characters)"
    )
    
    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that text is not just whitespace"""
        if not v.strip():
            raise ValueError('Text cannot be empty or only whitespace')
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Artificial intelligence is transforming industries across the globe. From healthcare to finance, AI systems are being deployed to improve efficiency, reduce costs, and enhance decision-making capabilities."
                }
            ]
        }
    }


class CityRequest(BaseModel):
    """Request model for city-based endpoints"""
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
        # Capitalize each word (e.g., "new york" -> "New York")
        return v.strip().title()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"city": "Riyadh"},
                {"city": "London"},
                {"city": "Tokyo"}
            ]
        }
    }


class WeatherResponse(BaseModel):
    """Response model for weather data"""
    city: str = Field(..., description="City name")
    temperature: float = Field(..., description="Current temperature")
    unit: str = Field(default="°C", description="Temperature unit")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "city": "Riyadh",
                    "temperature": 32.1,
                    "unit": "°C"
                }
            ]
        }
    }


class SummaryResponse(BaseModel):
    """Response model for AI summarization"""
    summary: str = Field(..., description="AI-generated summary")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Artificial intelligence is revolutionizing multiple industries by improving efficiency and decision-making processes in sectors like healthcare and finance."
                }
            ]
        }
    }


class WeatherSummaryResponse(BaseModel):
    """Response model for combined weather + AI summary"""
    city: str = Field(..., description="City name")
    temperature: float = Field(..., description="Current temperature")
    unit: str = Field(default="°C", description="Temperature unit")
    summary: str = Field(..., description="AI-generated weather description")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "city": "Jeddah",
                    "temperature": 34.5,
                    "unit": "°C",
                    "summary": "It's a sunny day in Jeddah with warm temperatures around 34°C — perfect for the beach! The pleasant weather makes it ideal for outdoor activities."
                }
            ]
        }
    }