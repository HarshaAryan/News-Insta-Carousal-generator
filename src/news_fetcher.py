from tavily import TavilyClient
from config import TAVILY_API_KEY, JSON_TEMP_DIR, get_logger
import datetime
import json
from pathlib import Path

logger = get_logger("NewsFetcher")

class NewsFetcher:
    def __init__(self):
        if not TAVILY_API_KEY:
            logger.error("TAVILY_API_KEY is missing!")
            raise ValueError("TAVILY_API_KEY not found in .env")
        self.tavily = TavilyClient(api_key=TAVILY_API_KEY)

    def get_top_news(self, query="latest news", country="us", page_size=1):
        """Fetches top news using Tavily Search.
        
        Credit optimization:
        - search_depth="basic": 1 credit (vs 2+ for advanced)
        - max_results=page_size for articles
        - include_images=True: No extra cost, returns images with the news
        
        Returns:
            Tuple of (articles_list, images_list)
        """
        try:
            logger.info(f"Searching Tavily for: '{query}' (max_results={page_size})")
            # Optimized Tavily search - 1 credit per call, includes images
            response = self.tavily.search(
                query=query,
                topic="news",
                search_depth="basic",  # CRITICAL: Keeps it at 1 credit
                include_images=True,  # Get news-related images in same call
                max_results=page_size
            )
            
            # Save raw Tavily response for debugging
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = JSON_TEMP_DIR / f"tavily_response_{timestamp}.json"
            with open(json_path, 'w') as f:
                json.dump(response, f, indent=2)
            logger.info(f"Saved raw Tavily response to: {json_path}")
            
            results = response.get("results", [])
            valid_articles = []
            
            for res in results:
                # Basic validation
                if not res.get("title") or not res.get("url"):
                    continue
                
                valid_articles.append({
                    "title": res.get("title"),
                    "description": res.get("content", ""),
                    "url": res.get("url"),
                    "source": res.get("domain", "Tavily"),
                    "publishedAt": res.get("published_date", datetime.datetime.now().isoformat())
                })
            
            # Get all images from Tavily response
            # NOTE: These images are related to the search query (e.g., if query is about Trump/WW3,
            # images will be related to that topic from the same news search)
            images = response.get("images", [])
            logger.info(f"✅ Fetched {len(valid_articles)} articles with {len(images)} related images.")
            logger.info(f"📸 All images are contextually related to query: '{query}'")
            
            return valid_articles, images

        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return [], []

    def find_image_for_topic(self, query):
        """
        Uses Tavily search to specifically find an image for a query.
        Optimized for 1 credit per call.
        """
        try:
            response = self.tavily.search(
                query=query,
                search_depth="basic",  # 1 credit
                include_images=True,
                max_results=1  # Minimal results for image search
            )
            images = response.get("images", [])
            if images:
                return images[0]
            return None
        except Exception as e:
            logger.error(f"Error finding image: {e}")
            return None
    
    def get_news_images(self, query, num_images=5):
        """
        Fetches multiple news-related images from Tavily.
        Returns a list of image URLs related to the news topic.
        
        Args:
            query: News topic to search for images
            num_images: Number of images to fetch (default 5 for carousel)
        
        Returns:
            List of image URLs
        """
        try:
            logger.info(f"Fetching {num_images} news images for: {query}")
            response = self.tavily.search(
                query=query,
                topic="news",
                search_depth="basic",  # 1 credit
                include_images=True,
                max_results=num_images  # Get more results to ensure we have enough images
            )
            
            images = response.get("images", [])
            logger.info(f"Tavily returned {len(images)} images")
            
            # Return up to num_images, or pad with duplicates if needed
            if len(images) >= num_images:
                return images[:num_images]
            elif images:
                # Pad with duplicates if we don't have enough unique images
                while len(images) < num_images:
                    images.append(images[len(images) % len(images)])
                return images[:num_images]
            else:
                logger.warning("No images returned from Tavily")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching news images: {e}")
            return []        
