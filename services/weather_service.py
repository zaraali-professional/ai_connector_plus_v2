# weather_service.py
# Weather Service - Integrates with Open-Meteo API
# Fetches real-time weather data for major cities


import asyncio
import logging
import time
from typing import Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class WeatherService:
    
    # Service to fetch weather data from Open-Meteo API
    
    # Major cities with their coordinates (latitude, longitude)
    CITY_COORDINATES = {
        "Riyadh": (24.7136, 46.6753),
        "Jeddah": (21.4858, 39.1925),
        "Mecca": (21.3891, 39.8579),
        "Medina": (24.5247, 39.5692),
        "Dammam": (26.4207, 50.0888),
        "Dubai": (25.2048, 55.2708),
        "Abu Dhabi": (24.4539, 54.3773),
        "London": (51.5074, -0.1278),
        "Paris": (48.8566, 2.3522),
        "New York": (40.7128, -74.0060),
        "Tokyo": (35.6762, 139.6503),
        "Mumbai": (19.0760, 72.8777),
        "Cairo": (30.0444, 31.2357),
        "Sydney": (-33.8688, 151.2093),
        "Toronto": (43.6532, -79.3832),
        "Berlin": (52.5200, 13.4050),
        "Moscow": (55.7558, 37.6173),
        "Beijing": (39.9042, 116.4074),
        "Singapore": (1.3521, 103.8198),
        "Istanbul": (41.0082, 28.9784),
    }
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Cache TTL in seconds (5 minutes)
    CACHE_TTL = 300
    
    def __init__(self):
        """Initialize the weather service with an HTTP client and cache"""
        self.client = httpx.AsyncClient(timeout=10.0)
        self._cache_lock = asyncio.Lock()
        # Cache structure: {city_name: {"data": {...}, "timestamp": float}}
        self._cache: Dict[str, Dict] = {}
        logger.info("Weather service initialized with cache layer")
    
    async def close(self):
        """Close the HTTP client (cleanup)"""
        await self.client.aclose()
        logger.info("Weather service closed")
    
    def _get_coordinates(self, city: str) -> tuple[float, float]:
      
        # Get coordinates for a city
        
        # Args:
        #     city: City name (case-insensitive)
        
        # Returns:
        #     Tuple of (latitude, longitude)
        
        # Raises:
        #     ValueError: If city is not found
     
        # Normalize city name (capitalize)
        city_normalized = city.strip().title()
        
        if city_normalized not in self.CITY_COORDINATES:
            available_cities = ", ".join(sorted(self.CITY_COORDINATES.keys()))
            raise ValueError(
                f"City '{city}' not found. Available cities: {available_cities}"
            )
        
        return self.CITY_COORDINATES[city_normalized]
    
    async def _get_cached_weather(self, city: str) -> Optional[Dict[str, any]]:
        """
        Get weather data from cache if available and not expired
        
        Args:
            city: Normalized city name
            
        Returns:
            Cached weather data if valid, None otherwise
        """
        async with self._cache_lock:
            if city not in self._cache:
                return None
            
            cache_entry = self._cache[city]
            current_time = time.time()
            elapsed_time = current_time - cache_entry["timestamp"]
            
            if elapsed_time > self.CACHE_TTL:
                # Cache expired, remove it
                del self._cache[city]
                logger.debug(f"Cache expired for {city} (elapsed: {elapsed_time:.1f}s)")
                return None
            
            logger.info(f"Cache hit for {city} (age: {elapsed_time:.1f}s)")
            return cache_entry["data"]
    
    async def _store_in_cache(self, city: str, weather_data: Dict[str, any]):
        """
        Store weather data in cache with current timestamp
        
        Args:
            city: Normalized city name
            weather_data: Weather data dictionary to cache
        """
        async with self._cache_lock:
            self._cache[city] = {
                "data": weather_data,
                "timestamp": time.time()
            }
            logger.debug(f"Weather data cached for {city}")
    
    async def get_weather(self, city: str) -> Dict[str, any]:
      
        # Fetch current weather for a city
        
        # Args:
        #     city: Name of the city
        
        # Returns:
        #     Dictionary with city, temperature, and unit
        
        # Example:
        #     >>> weather = await weather_service.get_weather("Riyadh")
        #     >>> print(weather)
        #     {"city": "Riyadh", "temperature": 32.1, "unit": "°C"}
        
        try:
            # Step 1: Normalize city name
            city_normalized = city.strip().title()
            
            # Step 2: Check cache first
            cached_data = await self._get_cached_weather(city_normalized)
            if cached_data is not None:
                return cached_data
            
            # Step 3: Get coordinates for the city
            latitude, longitude = self._get_coordinates(city)
            
            logger.info(f"Fetching weather for {city_normalized} ({latitude}, {longitude}) from API")
            
            # Step 4: Build API request parameters
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",  
                "temperature_unit": "celsius"  
            }
            
            # Step 5: Make API request
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()  # Raise exception if status code is 4xx or 5xx
            
            # Step 6: Parse response
            data = response.json()
            
            if "current_weather" not in data:
                raise ValueError("Invalid response from weather API")
            
            current_weather = data["current_weather"]
            temperature = current_weather["temperature"]
            
            # Step 7: Build weather data response
            weather_data = {
                "city": city_normalized,
                "temperature": temperature,
                "unit": "°C"
            }
            
            # Step 8: Store in cache
            await self._store_in_cache(city_normalized, weather_data)
            
            logger.info(f"Weather fetched successfully: {city_normalized} = {temperature}°C")
            
            return weather_data
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching weather: {e}")
            raise ValueError(f"Failed to fetch weather data: {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error(f"Network error fetching weather: {e}")
            raise ValueError("Failed to connect to weather service")
        
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            raise
    
    @classmethod
    def get_available_cities(cls) -> list[str]:
      
        # Get list of all available cities
        
        # Returns:
        #     Sorted list of city names
    
        return sorted(cls.CITY_COORDINATES.keys())