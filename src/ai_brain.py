from google import genai
import json
from pathlib import Path
from config import GEMINI_API_KEY, get_logger

logger = get_logger("AIBrain")

class AIBrain:
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is missing!")
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        # Use the new google-genai client
        self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def generate_random_news_query(self):
        """
        Generates a random, trending news query to keep content fresh.
        Returns different queries for each run.
        """
        prompt = """
        Generate ONE random, trending news search query for today.
        Focus on: breaking news, viral stories, trending topics, major events.
        Categories: politics, technology, business, entertainment, world events, science.
        
        Return ONLY the search query text (5-8 words max), no JSON, no quotes.
        Examples: "Trump latest announcement", "AI breakthrough technology news", "stock market crash today"
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            query = response.text.strip().replace('"', '').replace("'", '')
            logger.info(f"Generated random query: {query}")
            return query
        except Exception as e:
            logger.error(f"Error generating random query: {e}")
            return "breaking news today"  # Fallback

    def analyze_virality(self, news_items):
        """
        Analyzes a list of news items.
        """
        prompt = f"""
        Analyze these news headlines and rank them by 'Virality Potential' (0-10) for IG.
        News Items: {json.dumps(news_items, default=str)}
        Return ONLY valid JSON: {{ "best_article_index": 0, "score": 9.5, "reason": "..." }}
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            text = self._clean_json(response.text)
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error in analyze_virality: {e}")
            return None

    def generate_carousel_script(self, article, reference_image_path=None, use_ai_images=False):
        """
        Generates prompts for 5 slides.
        
        Args:
            article: News article dict
            reference_image_path: Optional reference image
            use_ai_images: If True, generate image prompts. If False, generate text only.
        """
        
        if use_ai_images:
            # Generate detailed image generation prompts
            prompt_text = f"""
            Create a 5-slide Instagram Carousel script for this news:
            Headline: {article['title']}
            Summary: {article.get('description', '')}
            
            Generate 5 image generation prompts that include text rendering instructions.
            Return ONLY valid JSON:
            {{
                "slides": [
                    {{"slide_number": 1, "image_prompt": "..."}},
                    ...
                ]
            }}
            """
        else:
            # Generate text-only for Pillow overlay
            prompt_text = f"""
            Create a viral 5-slide Instagram Carousel script for this news:
            Headline: {article['title']}
            Summary: {article.get('description', '')}
            
            Style: Photo-first. Minimal text overlay. Punchy. Gen Z tone.
            
            Slide 1 (Cover): Hook with the main headline (max 10 words)
            Slides 2-4 (Content): Key details, one per slide (max 15 words each)
            Slide 5 (CTA): Call to action like "Follow for Daily News" (max 8 words)
            
            Return ONLY valid JSON:
            {{
                "slides": [
                    {{"slide_number": 1, "text": "BREAKING: Major announcement shakes industry"}},
                    {{"slide_number": 2, "text": "Key detail about the news"}},
                    {{"slide_number": 3, "text": "Why this matters to you"}},
                    {{"slide_number": 4, "text": "What happens next"}},
                    {{"slide_number": 5, "text": "Follow for Daily Tech News"}}
                ]
            }}
            """
        
        try:
            # Temporarily skip reference image to get basic flow working
            # TODO: Add back image upload once we verify core workflow
            response = self.client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt_text
            )
            
            text = self._clean_json(response.text)
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return None

    def _clean_json(self, text):
        return text.replace("```json", "").replace("```", "").strip()
