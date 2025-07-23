"""
Azure OpenAI Client Service
Provides a centralized client for Azure OpenAI API interactions
"""

import asyncio
from typing import Dict, Any, Optional, List
from openai import AsyncAzureOpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Azure OpenAI client for handling AI-powered features"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        try:
            if not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
                logger.warning("Azure OpenAI credentials not configured. AI features will be limited.")
                return
            
            self.client = AsyncAzureOpenAI(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version
            )
            logger.info("Azure OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            self.client = None
    
    async def generate_lyrics(
        self,
        title: str,
        genre: str,
        theme: Optional[str] = None,
        style: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Generate song lyrics using Azure OpenAI"""
        
        if not self.client:
            raise Exception("Azure OpenAI client not initialized. Check your configuration.")
        
        try:
            # Build the prompt
            if custom_prompt:
                prompt = f"""Create song lyrics based on this prompt: {custom_prompt}
                
Title: {title}
Genre: {genre}
Theme: {theme or 'General'}
Style: {style or 'Standard'}

Please create complete song lyrics with verses, chorus, and bridge. Make them creative and engaging."""
            else:
                prompt = f"""Create song lyrics for a {genre} song titled "{title}".

Theme: {theme or 'General'}
Style: {style or 'Standard'}

Please create complete song lyrics with:
- 2-3 verses
- A catchy chorus (repeated)
- A bridge section
- Appropriate structure for the {genre} genre

Make the lyrics creative, meaningful, and suitable for the theme "{theme or 'General'}"."""

            response = await self.client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional songwriter and lyricist. Create engaging, creative, and well-structured song lyrics that match the requested genre and theme."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=settings.azure_openai_max_tokens,
                temperature=settings.azure_openai_temperature
            )
            
            lyrics = response.choices[0].message.content.strip()
            return lyrics
            
        except Exception as e:
            logger.error(f"Failed to generate lyrics with Azure OpenAI: {e}")
            raise Exception(f"Failed to generate lyrics: {str(e)}")
    
    async def enhance_lyrics(self, existing_lyrics: str, enhancement_request: str) -> str:
        """Enhance existing lyrics based on user request"""
        
        if not self.client:
            raise Exception("Azure OpenAI client not initialized. Check your configuration.")
        
        try:
            prompt = f"""Please enhance these song lyrics based on the following request: {enhancement_request}

Current lyrics:
{existing_lyrics}

Enhancement request: {enhancement_request}

Please provide the enhanced version of the lyrics, maintaining the original structure but improving according to the request."""

            response = await self.client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional songwriter and lyricist. Enhance existing lyrics while maintaining their essence and structure."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=settings.azure_openai_max_tokens,
                temperature=settings.azure_openai_temperature
            )
            
            enhanced_lyrics = response.choices[0].message.content.strip()
            return enhanced_lyrics
            
        except Exception as e:
            logger.error(f"Failed to enhance lyrics with Azure OpenAI: {e}")
            raise Exception(f"Failed to enhance lyrics: {str(e)}")
    
    async def analyze_lyrics_sentiment(self, lyrics: str) -> Dict[str, Any]:
        """Analyze the sentiment and themes of lyrics"""
        
        if not self.client:
            raise Exception("Azure OpenAI client not initialized. Check your configuration.")
        
        try:
            prompt = f"""Analyze the following song lyrics and provide a detailed analysis:

Lyrics:
{lyrics}

Please provide analysis in the following JSON format:
{{
    "overall_sentiment": "positive/negative/neutral",
    "emotional_tone": "description of emotional tone",
    "main_themes": ["theme1", "theme2", "theme3"],
    "mood": "description of mood",
    "target_audience": "description of likely audience",
    "lyrical_quality": "assessment of lyrical quality",
    "suggestions": ["suggestion1", "suggestion2"]
}}"""

            response = await self.client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music industry expert and lyrical analyst. Provide detailed, professional analysis of song lyrics."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON, fallback to text analysis if needed
            try:
                import json
                analysis = json.loads(analysis_text)
            except:
                # Fallback to structured text analysis
                analysis = {
                    "overall_sentiment": "neutral",
                    "emotional_tone": "Unable to parse detailed analysis",
                    "main_themes": ["general"],
                    "mood": "Unknown",
                    "target_audience": "General",
                    "lyrical_quality": "Analysis available in raw format",
                    "suggestions": ["Review raw analysis"],
                    "raw_analysis": analysis_text
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze lyrics with Azure OpenAI: {e}")
            raise Exception(f"Failed to analyze lyrics: {str(e)}")
    
    async def generate_song_concept(self, genre: str, mood: str, keywords: List[str]) -> Dict[str, Any]:
        """Generate a complete song concept including title, theme, and structure"""
        
        if not self.client:
            raise Exception("Azure OpenAI client not initialized. Check your configuration.")
        
        try:
            keywords_str = ", ".join(keywords) if keywords else "creative, original"
            
            prompt = f"""Create a complete song concept for a {genre} song with a {mood} mood.

Keywords to incorporate: {keywords_str}

Please provide a detailed song concept in the following JSON format:
{{
    "title": "Song Title",
    "theme": "Main theme of the song",
    "story": "Brief story or message of the song",
    "structure": {{
        "verse_count": 2,
        "has_pre_chorus": false,
        "has_bridge": true,
        "has_outro": false
    }},
    "key_elements": ["element1", "element2", "element3"],
    "target_emotion": "emotion to evoke",
    "lyrical_approach": "description of lyrical style",
    "suggested_tempo": "slow/medium/fast",
    "inspiration": "brief description of inspiration"
}}"""

            response = await self.client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative music producer and songwriter. Generate innovative and marketable song concepts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.8  # Higher temperature for more creativity
            )
            
            concept_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                import json
                concept = json.loads(concept_text)
            except:
                # Fallback concept
                concept = {
                    "title": f"Untitled {genre} Song",
                    "theme": mood.capitalize(),
                    "story": "A song about life experiences",
                    "structure": {
                        "verse_count": 2,
                        "has_pre_chorus": False,
                        "has_bridge": True,
                        "has_outro": False
                    },
                    "key_elements": keywords,
                    "target_emotion": mood,
                    "lyrical_approach": f"{genre} style with {mood} mood",
                    "suggested_tempo": "medium",
                    "inspiration": "Generated concept",
                    "raw_concept": concept_text
                }
            
            return concept
            
        except Exception as e:
            logger.error(f"Failed to generate song concept with Azure OpenAI: {e}")
            raise Exception(f"Failed to generate song concept: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Azure OpenAI client is available"""
        return self.client is not None


# Global instance
azure_openai_client = AzureOpenAIClient()
