from openai import AsyncOpenAI
from typing import Dict, Any, Optional
from ...core.config import settings


class LyricsGenerator:
    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_lyrics(
        self,
        title: str,
        genre: str,
        theme: Optional[str] = None,
        style: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate song lyrics using OpenAI GPT"""
        
        if not self.client:
            # Fallback to demo lyrics if no API key
            return self._generate_demo_lyrics(title, genre, theme, style)
        
        # Build the prompt
        prompt = self._build_lyrics_prompt(title, genre, theme, style, custom_prompt)
        
        try:
            response = await self.client.chat.completions.create(
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
    
    def _generate_demo_lyrics(
        self,
        title: str,
        genre: str,
        theme: Optional[str] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate demo lyrics when OpenAI API is not available"""
        
        # Create genre-specific demo lyrics
        demo_lyrics_templates = {
            "Pop": """Verse 1:
Walking down the street tonight
Everything feels so right
{theme} is calling out my name
Nothing will ever be the same

Chorus:
{title}, {title}
Dancing in the moonlight
{title}, {title}
Everything's gonna be alright

Verse 2:
Stars are shining up above
This feeling that I'm thinking of
{theme} is all I need to know
Together we will steal the show

Chorus:
{title}, {title}
Dancing in the moonlight
{title}, {title}
Everything's gonna be alright

Bridge:
When the world gets heavy
And the road gets long
We'll remember this moment
In our favorite song

Chorus:
{title}, {title}
Dancing in the moonlight
{title}, {title}
Everything's gonna be alright""",
            
            "Rock": """Verse 1:
Thunder rolling in the night
Ready for the coming fight
{theme} burning in my soul
Rock and roll is my control

Chorus:
{title}! {title}!
Screaming loud and free
{title}! {title}!
This is who I'm meant to be

Verse 2:
Electric guitars blazing high
Reaching for the endless sky
{theme} pumping through my veins
Breaking free from all the chains

Chorus:
{title}! {title}!
Screaming loud and free
{title}! {title}!
This is who I'm meant to be

Bridge:
When the darkness falls around
We'll make that thunderous sound
Nothing's gonna stop us now
We'll show them all just how

Chorus:
{title}! {title}!
Screaming loud and free
{title}! {title}!
This is who I'm meant to be""",
            
            "Blues": """Verse 1:
Woke up this morning, feeling so low
{theme} got me down, nowhere to go
{title} is all I got left to say
Blues gonna wash my pain away

Chorus:
Oh {title}, {title}
Why you gotta be so cruel
{title}, {title}
Playing me just like a fool

Verse 2:
Rain keeps falling on my door
Can't take this heartache anymore
{theme} is haunting all my dreams
Nothing's ever what it seems

Chorus:
Oh {title}, {title}
Why you gotta be so cruel
{title}, {title}
Playing me just like a fool

Bridge:
Someday the sun will shine again
Till then I'll sing about my pain
These blues will help me find my way
To see a brighter, better day

Chorus:
Oh {title}, {title}
Why you gotta be so cruel
{title}, {title}
Playing me just like a fool"""
        }
        
        # Get template for genre or default to Pop
        template = demo_lyrics_templates.get(genre, demo_lyrics_templates["Pop"])
        
        # Replace placeholders
        lyrics = template.format(
            title=title,
            theme=theme or "love"
        )
        
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
                "estimated_duration": self._estimate_duration(lyrics),
                "demo_mode": True
            }
        }
