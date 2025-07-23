import asyncio
import random
from typing import Dict, Any, Optional, List

class LyricsGenerator:
    """Lyrics generation service for creating song lyrics"""
    
    def __init__(self):
        self.verse_templates = self._load_verse_templates()
        self.chorus_templates = self._load_chorus_templates()
        self.bridge_templates = self._load_bridge_templates()
        self.rhyme_schemes = self._load_rhyme_schemes()
    
    def _load_verse_templates(self) -> Dict[str, List[str]]:
        """Load verse templates by genre and theme"""
        return {
            'Pop': {
                'Love': [
                    "Walking down the street, thinking of you\nEvery step I take, my heart beats true\nMemories of us, they fill my mind\nA love like ours is hard to find",
                    "In the morning light, I see your face\nEvery moment with you, time can't erase\nYou're the melody in my heart's song\nWith you is where I belong"
                ],
                'Freedom': [
                    "Breaking free from all the chains\nNo more living with the pains\nSpread my wings and touch the sky\nNow's the time to learn to fly",
                    "Open roads and endless dreams\nNothing's quite the way it seems\nLeaving all my fears behind\nPeace and freedom I will find"
                ]
            },
            'Rock': {
                'Rebellion': [
                    "They try to tell us what to do\nBut we won't listen, we'll break through\nStanding up for what is right\nWe'll keep on fighting through the night",
                    "System's broken, can't you see\nTime to set our spirits free\nRaise your voice and make it loud\nStand up tall and be proud"
                ],
                'Power': [
                    "Thunder rolling in the sky\nLightning flashing way up high\nFeel the power in your soul\nTake control and reach your goal",
                    "Mountains crumble at our feet\nNothing can our will defeat\nStrength and courage guide our way\nThis is our victorious day"
                ]
            }
        }
    
    def _load_chorus_templates(self) -> Dict[str, List[str]]:
        """Load chorus templates by genre and theme"""
        return {
            'Pop': {
                'Love': [
                    "You're my sunshine, you're my rain\nYou're the cure for all my pain\nTogether we can face it all\nTogether we will never fall",
                    "Love is all we need tonight\nEverything will be alright\nHold me close and don't let go\nYou're the only one I know"
                ],
                'Freedom': [
                    "We are free, we are alive\nWatch us soar, watch us thrive\nNothing's gonna hold us down\nWe're the kings without a crown",
                    "Freedom calls our name tonight\nSpread our wings and take to flight\nBreak the chains and touch the stars\nThe world is ours, the world is ours"
                ]
            },
            'Rock': {
                'Rebellion': [
                    "We won't back down, we won't give in\nThis is where our fight begins\nStand together, stand as one\nOur revolution has begun",
                    "Break the walls and tear them down\nWe're the rebels in this town\nFight for freedom, fight for truth\nWe are the voice of youth"
                ],
                'Power': [
                    "Feel the power, feel the might\nWe are warriors in the night\nNothing's gonna stop us now\nWe'll show them all just how",
                    "Power flows through every vein\nWe will rise through joy and pain\nUnstoppable, unbreakable\nOur spirit's unshakeable"
                ]
            }
        }
    
    def _load_bridge_templates(self) -> List[str]:
        """Load bridge templates"""
        return [
            "When the world gets dark and cold\nAnd the story's left untold\nWe'll find a way to make it right\nGuided by our inner light",
            "Through the storms and through the rain\nThrough the joy and through the pain\nWe'll keep moving, we'll stay strong\nThis is where we all belong",
            "Time keeps moving, seasons change\nNothing ever stays the same\nBut the fire in our hearts\nIs where our journey really starts"
        ]
    
    def _load_rhyme_schemes(self) -> Dict[str, str]:
        """Load rhyme schemes by genre"""
        return {
            'Pop': 'ABAB',
            'Rock': 'AABB',
            'Hip Hop': 'ABAB',
            'R&B': 'ABCB',
            'Country': 'ABAB',
            'Electronic': 'AABB'
        }
    
    async def generate_lyrics(
        self,
        title: str,
        genre: str,
        theme: Optional[str] = None,
        style: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate complete song lyrics"""
        
        try:
            # Use custom prompt if provided, otherwise use templates
            if custom_prompt:
                lyrics = await self._generate_from_prompt(custom_prompt, title, genre)
            else:
                lyrics = await self._generate_from_templates(title, genre, theme, style)
            
            # Parse lyrics structure
            structure = self._parse_lyrics_structure(lyrics)
            
            # Calculate metadata
            word_count = len(lyrics.split())
            estimated_duration = max(120, int(word_count / 2.5))  # ~2.5 words per second
            
            return {
                'lyrics': lyrics,
                'structure': structure,
                'metadata': {
                    'title': title,
                    'genre': genre,
                    'theme': theme,
                    'style': style,
                    'word_count': word_count,
                    'estimated_duration': estimated_duration,
                    'rhyme_scheme': self.rhyme_schemes.get(genre, 'ABAB'),
                    'has_custom_prompt': custom_prompt is not None
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate lyrics: {str(e)}")
    
    async def _generate_from_prompt(self, prompt: str, title: str, genre: str) -> str:
        """Generate lyrics from custom prompt"""
        # For now, create a simple structure incorporating the prompt
        # In a real implementation, this would use an AI model
        
        verse1 = f"In the world of {prompt.lower()}\nWhere dreams and reality meet\nI find myself searching for meaning\nIn every rhythm and beat"
        
        chorus = f"This is my song about {prompt.lower()}\nLet the music set me free\n{title} is calling out my name\nThis is who I'm meant to be"
        
        verse2 = f"Through the melodies of {prompt.lower()}\nI discover who I am\nEvery note tells a story\nOf this life's eternal plan"
        
        bridge = f"When the {prompt.lower()} fades away\nAnd silence fills the air\nI'll remember this moment\nAnd the music we shared"
        
        return f"{verse1}\n\n{chorus}\n\n{verse2}\n\n{chorus}\n\n{bridge}\n\n{chorus}"
    
    async def _generate_from_templates(self, title: str, genre: str, theme: str, style: str) -> str:
        """Generate lyrics from templates"""
        
        # Get templates for genre and theme
        verse_templates = self.verse_templates.get(genre, {}).get(theme, [])
        chorus_templates = self.chorus_templates.get(genre, {}).get(theme, [])
        
        # Fallback to Pop templates if genre/theme not found
        if not verse_templates:
            verse_templates = self.verse_templates.get('Pop', {}).get('Love', [
                "Walking through life with hope in my heart\nEvery day feels like a brand new start\nDreams and wishes guide my way\nToday's the beginning of a brighter day"
            ])
        
        if not chorus_templates:
            chorus_templates = self.chorus_templates.get('Pop', {}).get('Love', [
                f"{title} is the song I sing\n{title} makes my heart take wing\nEvery moment, every day\n{title} lights up my way"
            ])
        
        # Select random templates
        verse1 = random.choice(verse_templates)
        verse2 = random.choice(verse_templates) if len(verse_templates) > 1 else verse1
        chorus = random.choice(chorus_templates)
        bridge = random.choice(self.bridge_templates)
        
        # Customize with title
        chorus = chorus.replace("You're my sunshine", f"{title} is my sunshine")
        chorus = chorus.replace("Love is all", f"{title} is all")
        
        # Structure: Verse - Chorus - Verse - Chorus - Bridge - Chorus
        return f"{verse1}\n\n{chorus}\n\n{verse2}\n\n{chorus}\n\n{bridge}\n\n{chorus}"
    
    def _parse_lyrics_structure(self, lyrics: str) -> Dict[str, Any]:
        """Parse the structure of generated lyrics"""
        
        sections = lyrics.split('\n\n')
        structure = {
            'sections': [],
            'total_sections': len(sections),
            'estimated_verses': 0,
            'estimated_choruses': 0,
            'has_bridge': False
        }
        
        for i, section in enumerate(sections):
            lines = len(section.split('\n'))
            
            # Simple heuristic to identify section types
            if i == 0 or i == 2:  # Typically verses
                structure['sections'].append({
                    'type': 'verse',
                    'index': i,
                    'lines': lines,
                    'content_preview': section[:50] + '...' if len(section) > 50 else section
                })
                structure['estimated_verses'] += 1
            elif 'bridge' in section.lower() or i == len(sections) - 2:  # Bridge typically before final chorus
                structure['sections'].append({
                    'type': 'bridge',
                    'index': i,
                    'lines': lines,
                    'content_preview': section[:50] + '...' if len(section) > 50 else section
                })
                structure['has_bridge'] = True
            else:  # Likely chorus
                structure['sections'].append({
                    'type': 'chorus',
                    'index': i,
                    'lines': lines,
                    'content_preview': section[:50] + '...' if len(section) > 50 else section
                })
                structure['estimated_choruses'] += 1
        
        return structure
    
    async def generate_verse(self, theme: str, genre: str) -> str:
        """Generate a single verse"""
        verse_templates = self.verse_templates.get(genre, {}).get(theme, [])
        if not verse_templates:
            verse_templates = ["Life is a journey we all must take\nEvery step forward for our own sake\nThrough the good times and the bad\nWe'll remember what we've had"]
        
        return random.choice(verse_templates)
    
    async def generate_chorus(self, title: str, theme: str, genre: str) -> str:
        """Generate a single chorus"""
        chorus_templates = self.chorus_templates.get(genre, {}).get(theme, [])
        if not chorus_templates:
            chorus_templates = [f"{title} is the song we sing\n{title} makes our hearts take wing\nEvery moment of every day\n{title} shows us the way"]
        
        chorus = random.choice(chorus_templates)
        return chorus.replace("You're my", f"{title} is my").replace("Love is", f"{title} is")
    
    def analyze_lyrics(self, lyrics: str) -> Dict[str, Any]:
        """Analyze lyrics for various metrics"""
        
        words = lyrics.split()
        lines = lyrics.split('\n')
        
        # Basic metrics
        word_count = len(words)
        line_count = len([line for line in lines if line.strip()])
        avg_words_per_line = word_count / line_count if line_count > 0 else 0
        
        # Sentiment analysis (simplified)
        positive_words = ['love', 'happy', 'joy', 'bright', 'hope', 'dream', 'free', 'beautiful', 'amazing']
        negative_words = ['sad', 'pain', 'hurt', 'dark', 'broken', 'lost', 'fear', 'alone', 'cry']
        
        positive_count = sum(1 for word in words if word.lower() in positive_words)
        negative_count = sum(1 for word in words if word.lower() in negative_words)
        
        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Complexity analysis
        unique_words = len(set(word.lower() for word in words))
        vocabulary_richness = unique_words / word_count if word_count > 0 else 0
        
        return {
            'word_count': word_count,
            'line_count': line_count,
            'avg_words_per_line': round(avg_words_per_line, 2),
            'unique_words': unique_words,
            'vocabulary_richness': round(vocabulary_richness, 3),
            'sentiment': sentiment,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'estimated_reading_time': round(word_count / 200, 2),  # 200 words per minute
            'estimated_singing_time': round(word_count / 150, 2)   # Slower for singing
        }
