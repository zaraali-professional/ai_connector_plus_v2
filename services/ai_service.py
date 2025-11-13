
# AI Service - Integrates with OpenAI API for text summarization
# Uses GPT-3.5-turbo for cost-effective and fast summarization


import os
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Loading environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    
    # Service to interact with OpenAI API for text summarization
    
    # Uses GPT-3.5-turbo model for efficient and affordable text processing
    
    
    def __init__(self):
        
        # Initialize the AI service with OpenAI client
        
        # Raises:
        #     ValueError: If Open api key is not set
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError(
                "OPENAI_API_KEY not set. Please add it to your .env file:\n"
                "OPENAI_API_KEY=sk-your-api-key-here"
            )
        
        # Initialize async OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info("AI service initialized with OpenAI")
    
    async def close(self):
        """Close the OpenAI client (cleanup)"""
        await self.client.close()
        logger.info("AI service closed")
    
    async def summarize_text(self, text: str, max_tokens: int = 150) -> str:
        """
        Summarize text using OpenAI GPT-3.5-turbo
        
        Args:
            text: The text to summarize
            max_tokens: Maximum length of summary (default: 150)
        
        Returns:
            AI-generated summary
        
        Example:
            >>> summary = await ai_service.summarize_text("Long article...")
            >>> print(summary)
            "This article discusses..."
        """
        try:
            logger.info(f"Generating summary for text (length: {len(text)} chars)")
            
            # Create the prompt
            # For weather summaries, the text is already a prompt
            # For regular summarization, we add instructions
            if "temperature is" in text.lower() or "weather in" in text.lower():
                # This is a weather description request
                system_message = "You are a friendly weather reporter who describes weather in an engaging, conversational way."
                user_message = text
            else:
                # This is a regular text summarization request
                system_message = "You are a helpful assistant that creates concise, accurate summaries of text."
                user_message = f"Please summarize the following text in 2-3 sentences:\n\n{text}"
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7,  
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract the summary
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"Summary generated successfully (length: {len(summary)} chars)")
            logger.debug(f"Summary preview: {summary[:100]}...")
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            raise ValueError(f"Failed to generate AI summary: {str(e)}")
    
    async def chat(self, messages: list[dict], max_tokens: int = 500) -> str:
        """
        General chat completion method for custom use cases
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum response length
        
        Returns:
            AI-generated response
        
        Example:
            >>> messages = [
            ...     {"role": "user", "content": "What is FastAPI?"}
            ... ]
            >>> response = await ai_service.chat(messages)
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise ValueError(f"Failed to generate chat response: {str(e)}")

