import openai
from typing import Dict, Any, Optional
from ...core.config import settings


class LyricsGenerator:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key

    async def generate_lyrics(
        self,
        title: str,
        genre: str,
        theme: Optional[str] = None,
        style: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate song lyrics using OpenAI GPT"""
        
        # Build the prompt
        prompt = self._build_lyrics_prompt(title, genre, theme, style, custom_prompt)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional songwriter and lyricist. Create engaging, creative, and well-structured song lyrics that match the given requirements. Format the output with clear verse/chorus/bridge structure."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.8
            )
            
            lyrics = response.choices[0].message.content.strip()
            
            # Parse the lyrics structure
            parsed_lyrics = self._parse_lyrics_structure(lyrics)
            
            return {
                "lyrics": lyrics,
                "structure": parsed_lyrics,
                "metadata": {
                    "title": title,
                    "genre": genre,
                    "theme": theme,
                    "style": style,
                    "word_count": len(lyrics.split()),
                    "estimated_duration": self._estimate_duration(lyrics)
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate lyrics: {str(e)}")

    def _build_lyrics_prompt(
        self,
        title: str,
        genre: str,
        theme: Optional[str],
        style: Optional[str],
        custom_prompt: Optional[str]
    ) -> str:
        """Build the prompt for lyrics generation"""
        
        prompt = f"Write song lyrics for a {genre} song titled '{title}'."
        
        if theme:
            prompt += f" The theme should be about {theme}."
        
        if style:
            prompt += f" The style should be {style}."
        
        if custom_prompt:
            prompt += f" Additional requirements: {custom_prompt}"
        
        prompt += """
        
Please structure the lyrics with:
- Verse 1
- Chorus
- Verse 2
- Chorus
- Bridge (optional)
- Chorus (final)

Make the lyrics engaging, memorable, and appropriate for the genre. Include emotional depth and vivid imagery.
"""
        
        return prompt

    def _parse_lyrics_structure(self, lyrics: str) -> Dict[str, Any]:
        """Parse the lyrics to identify structure"""
        lines = lyrics.split('\n')
        structure = {
            "verses": [],
            "chorus": [],
            "bridge": [],
            "sections": []
        }
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ['verse', 'chorus', 'bridge', 'intro', 'outro']):
                # Save previous section
                if current_section and current_content:
                    structure["sections"].append({
                        "type": current_section,
                        "content": '\n'.join(current_content)
                    })
                    
                    if current_section == "chorus":
                        structure["chorus"] = current_content.copy()
                    elif "verse" in current_section:
                        structure["verses"].append(current_content.copy())
                    elif current_section == "bridge":
                        structure["bridge"] = current_content.copy()
                
                # Start new section
                current_section = lower_line
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            structure["sections"].append({
                "type": current_section,
                "content": '\n'.join(current_content)
            })
        
        return structure

    def _estimate_duration(self, lyrics: str) -> float:
        """Estimate song duration based on lyrics length"""
        word_count = len(lyrics.split())
        # Rough estimate: average 2-3 words per second in songs
        estimated_seconds = word_count / 2.5
        return round(estimated_seconds, 1)
