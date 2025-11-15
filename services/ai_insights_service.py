"""
AI Insights Service - Intelligent Weather-Based Recommendations
Combines weather data with AI to generate context-aware, personalized insights
"""

import logging
from typing import Dict
from services.weather_service import WeatherService
from services.ai_service import AIService

logger = logging.getLogger(__name__)


class AIInsightsService:
    """
    Service that combines weather data with AI to generate intelligent insights
    
    This service acts as a bridge between weather and AI services,
    creating context-aware, personalized recommendations.
    """
    
    def __init__(self, weather_service: WeatherService, ai_service: AIService):
        """
        Initialize the insights service with dependencies
        
        Args:
            weather_service: Instance of WeatherService
            ai_service: Instance of AIService
        """
        self.weather_service = weather_service
        self.ai_service = ai_service
        logger.info("✨ AI Insights Service initialized")
    
    def _get_language_instruction(self, lang: str) -> str:
        """
        Get language-specific instructions for AI
        
        Args:
            lang: Language code
        
        Returns:
            Instruction text for the AI prompt
        """
        language_map = {
            "en": "English",
            "ar": "Arabic (العربية)",
            "es": "Spanish (Español)",
            "fr": "French (Français)",
            "de": "German (Deutsch)",
            "it": "Italian (Italiano)",
            "ja": "Japanese (日本語)",
            "zh-cn": "Chinese Simplified (简体中文)"
        }
        
        language_name = language_map.get(lang, "English")
        
        if lang == "en":
            return ""  # No extra instruction needed for English
        else:
            return f"\nIMPORTANT: Write your response in {language_name}. Use natural, native expressions."
    
    async def get_weather_insight(self, city: str) -> Dict[str, any]:
        """
        Generate a friendly, emoji-rich weather insight
        
        Args:
            city: City name
        
        Returns:
            Dictionary with city, temperature, and AI-generated insight
        
        Example:
            >>> insight = await service.get_weather_insight("Jeddah")
            >>> print(insight['insight'])
            "It's a sunny afternoon in Jeddah ☀️ — perfect for a beach walk!"
        """
        try:
            logger.info(f"🌤️ Generating weather insight for {city}")
            
            # Step 1: Get weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Step 2: Create AI prompt for weather insight
            prompt = f"""You are a friendly weather assistant. Describe today's weather in {weather_data['city']} 
where the temperature is {weather_data['temperature']}°C.

Requirements:
- Write 1-2 short, conversational sentences
- Include relevant emojis (☀️, 🌤️, ☁️, 🌧️, ❄️, 🌙, 🌸, etc.)
- Make it engaging and human-like
- Suggest what the weather is good for (e.g., "perfect for a walk", "great beach day")
- Keep it positive and upbeat
- DO NOT wrap your response in quotation marks
- Return ONLY the plain text description

Temperature guide:
- Above 35°C: Very hot
- 28-35°C: Hot/warm
- 20-28°C: Pleasant/nice
- 10-20°C: Cool
- Below 10°C: Cold

Example output: It's a sunny afternoon in Jeddah ☀️ — perfect for a beach walk or an iced coffee!

Now describe the weather (plain text only):"""
            
            # Step 3: Get AI-generated insight
            insight = await self.ai_service.summarize_text(prompt)
            
            # Step 4: Clean up any extra quotes that AI might add
            insight = insight.strip().strip('"').strip("'").strip()
            
            logger.info(f"✅ Weather insight generated for {city}")
            
            return {
                "city": weather_data["city"],
                "temperature": weather_data["temperature"],
                "unit": weather_data["unit"],
                "insight": insight
            }
        
        except Exception as e:
            logger.error(f"❌ Error generating weather insight: {str(e)}")
            raise
    
    async def get_mood_insight(self, city: str, mood: str) -> Dict[str, any]:
        """
        Generate mood-based personalized recommendation
        
        Args:
            city: City name
            mood: User's current mood (happy, tired, stressed, etc.)
        
        Returns:
            Dictionary with city, temperature, mood, and AI recommendation
        
        Example:
            >>> insight = await service.get_mood_insight("Cairo", "tired")
            >>> print(insight['recommendation'])
            "You're feeling tired and it's cozy 22°C in Cairo 🌙 — grab a warm drink!"
        """
        try:
            logger.info(f"💭 Generating mood-based insight for {city} (mood: {mood})")
            
            # Step 1: Get weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Step 2: Create mood-aware prompt
            prompt = f"""You are an empathetic AI companion. A user is feeling {mood} and is in {weather_data['city']} 
where the temperature is {weather_data['temperature']}°C.

User's mood: {mood}
Current weather: {weather_data['temperature']}°C in {weather_data['city']}

Requirements:
- Acknowledge their mood empathetically
- Combine their mood with the current weather
- Suggest a gentle, appropriate activity or recommendation
- Include 1-2 relevant emojis (🌙, ☕, 🌻, 💪, 🎉, 🌿, etc.)
- Keep it to 1-2 short sentences
- Be warm, caring, and human-like
- DO NOT wrap your response in quotation marks
- Return ONLY the plain text recommendation

Mood-specific suggestions:
- tired: Rest, cozy activities, warm drinks, gentle walks, relaxation
- stressed: Calming activities, nature, mindful moments, deep breaths
- happy: Enjoy the day, social activities, celebrate the moment
- energetic: Active pursuits, adventures, sports, outdoor fun
- sad: Comfort, self-care, gentle encouragement, small treats
- relaxed: Maintain the vibe, easy activities, peaceful moments
- excited: Channel the energy, fun activities, share the joy

Example output: You're feeling tired and it's a cozy 22°C in Cairo 🌙 — maybe grab a warm drink and unwind indoors.

Generate your recommendation (plain text only):"""
            
            # Step 3: Get AI recommendation
            recommendation = await self.ai_service.summarize_text(prompt)
            
            # Step 4: Clean up any extra quotes that AI might add
            recommendation = recommendation.strip().strip('"').strip("'").strip()
            
            logger.info(f"✅ Mood insight generated for {city}")
            
            return {
                "city": weather_data["city"],
                "temperature": weather_data["temperature"],
                "unit": weather_data["unit"],
                "mood": mood,
                "recommendation": recommendation
            }
        
        except Exception as e:
            logger.error(f"❌ Error generating mood insight: {str(e)}")
            raise
    
    async def get_activity_insight(self, city: str, activity_type: str) -> Dict[str, any]:
        """
        Generate activity-specific smart suggestions
        
        Args:
            city: City name
            activity_type: Type of activity (outdoor, workout, shopping, etc.)
        
        Returns:
            Dictionary with city, temperature, activity type, and AI suggestion
        
        Example:
            >>> insight = await service.get_activity_insight("Riyadh", "workout")
            >>> print(insight['suggestion'])
            "It's quite warm in Riyadh 🏃 — try an early-morning jog instead!"
        """
        try:
            logger.info(f"🏃 Generating activity insight for {city} (activity: {activity_type})")
            
            # Step 1: Get weather data
            weather_data = await self.weather_service.get_weather(city)
            temp = weather_data['temperature']
            
            # Step 2: Create activity-aware prompt
            prompt = f"""You are a helpful activity planner. Someone wants to do {activity_type} activities 
in {weather_data['city']} where it's currently {temp}°C.

Activity type: {activity_type}
Current weather: {temp}°C in {weather_data['city']}

Requirements:
- Give smart, weather-appropriate advice for this activity
- If weather isn't ideal, suggest alternatives or timing adjustments
- Include 1-2 relevant emojis (🏃, 🌞, 🛍️, 🍽️, 📸, 🧘, etc.)
- Keep it to 1-2 sentences
- Be practical and helpful
- DO NOT wrap your response in quotation marks
- Return ONLY the plain text suggestion

Activity-specific considerations:
- outdoor: Temperature comfort, sun protection, timing recommendations
- workout: Heat management, hydration, ideal exercise times
- shopping: Indoor vs outdoor malls, comfort considerations
- dining: Outdoor seating viability, weather enjoyment
- sightseeing: Walking comfort, photo opportunities, crowd considerations
- relaxing: Indoor vs outdoor relaxation spots, comfort

Temperature guidelines:
- Above 35°C: Suggest early morning/evening, air-conditioned spaces, hydration
- 28-35°C: Warn about heat, suggest shade/breaks, sun protection
- 20-28°C: Ideal for most activities, encourage outdoor plans
- 10-20°C: Suggest layers, mention pleasant coolness
- Below 10°C: Suggest warm clothing, indoor alternatives if needed

Example output: It's quite warm in Riyadh 🏃 — try an early-morning jog instead of mid-day exercise.

Generate your suggestion (plain text only):"""
            
            # Step 3: Get AI suggestion
            suggestion = await self.ai_service.summarize_text(prompt)
            
            # Step 4: Clean up any extra quotes that AI might add
            suggestion = suggestion.strip().strip('"').strip("'").strip()
            
            logger.info(f"✅ Activity insight generated for {city}")
            
            return {
                "city": weather_data["city"],
                "temperature": weather_data["temperature"],
                "unit": weather_data["unit"],
                "activity_type": activity_type,
                "suggestion": suggestion
            }
        
        except Exception as e:
            logger.error(f"❌ Error generating activity insight: {str(e)}")
            raise
    
    async def get_weather_insight_with_options(
        self, 
        city: str, 
        lang: str = "en",
        include_audio: bool = False,
        tts_service = None
    ) -> Dict[str, any]:
        """
        Generate weather insight with language and audio options
        
        Args:
            city: City name
            lang: Language code (en, ar, es, etc.)
            include_audio: Whether to generate audio file
            tts_service: TTS service instance
        
        Returns:
            Dictionary with insight and optional audio file path
        """
        try:
            logger.info(f"🌤️ Generating weather insight for {city} (lang: {lang})")
            
            # Get weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Create language-specific prompt
            lang_instruction = self._get_language_instruction(lang)
            
            prompt = f"""You are a friendly weather assistant. Describe today's weather in {weather_data['city']} 
where the temperature is {weather_data['temperature']}°C.

Requirements:
- Write 1-2 short, conversational sentences
- Include relevant emojis (☀️, 🌤️, ☁️, 🌧️, ❄️, 🌙)
- Make it engaging and human-like
- Suggest what the weather is good for
- Keep it positive and upbeat
- DO NOT wrap your response in quotation marks
- Return ONLY the plain text description{lang_instruction}

Example output: It's a sunny afternoon in Jeddah ☀️ — perfect for a beach walk or an iced coffee!

Now describe the weather (plain text only):"""
            
            # Get AI insight
            insight = await self.ai_service.summarize_text(prompt)
            insight = insight.strip().strip('"').strip("'").strip()
            
            result = {
                "city": weather_data["city"],
                "temperature": weather_data["temperature"],
                "unit": weather_data["unit"],
                "insight": insight,
                "language": lang
            }
            
            # Generate audio if requested
            if include_audio and tts_service:
                try:
                    audio_path = tts_service.text_to_speech(insight, lang)
                    result["audio_file"] = audio_path
                    logger.info(f"🔊 Audio generated for {city}")
                except Exception as e:
                    logger.error(f"Failed to generate audio: {e}")
                    result["audio_file"] = None
            
            logger.info(f"✅ Weather insight generated for {city}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Error generating weather insight: {str(e)}")
            raise