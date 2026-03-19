import argparse
import sys
from pathlib import Path
from src.news_fetcher import NewsFetcher
from src.ai_brain import AIBrain
from src.ai_image_gen import AIImageGenerator
from src.carousel_generator import CarouselGenerator
from src.daily_store import save_news_item, get_todays_items
from src.mailer import Mailer
from config import get_logger, BASE_DIR, CAROUSELS_DIR, IMAGE_TEMP_DIR, JSON_TEMP_DIR, USE_AI_IMAGE_GENERATION
import requests
import zipfile
import datetime
import json

logger = get_logger("Main")

def download_image(url, path):
    """Helper to download image from URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logger.error(f"Failed to download image: {e}")
        return False

def run_hourly_job():
    """Generate carousel posts from top news stories"""
    logger.info("Starting Hourly Job...")
    logger.info(f"Image Generation Mode: {'AI (Vertex)' if USE_AI_IMAGE_GENERATION else 'Pillow (Free)'}")
    
    nf = NewsFetcher()
    brain = AIBrain()
    mailer = Mailer()

    # 1. Generate random news query for variety
    random_query = brain.generate_random_news_query()
    logger.info(f"🎲 Random query: '{random_query}'")

    # 2. Fetch News from Tavily (1 credit per call with search_depth="basic")
    # For testing: page_size=1 (change to 10 for production)
    # This returns both articles AND related images in a single API call
    # Images are contextually related to the query (e.g., Trump news = Trump images)
    news_list, news_images = nf.get_top_news(query=random_query, page_size=1)
    if not news_list:
        logger.warning("No news found.")
        return

    # 3. Analyze Virality
    analysis = brain.analyze_virality(news_list)
    if not analysis:
        logger.error("Failed to analyze news.")
        return

    best_article = news_list[analysis["best_article_index"]]
    logger.info(f"Selected Article: {best_article['title']}")

    # 4. Ensure we have 5 images for carousel (pad if needed)
    if not news_images:
        logger.warning("No news images from Tavily, using fallback")
        news_images = ["https://images.unsplash.com/photo-1451187580459-43490279c0fa"] * 5
    elif len(news_images) < 5:
        logger.info(f"Only {len(news_images)} images from Tavily, padding to 5")
        # Repeat images to reach 5
        while len(news_images) < 5:
            news_images.append(news_images[len(news_images) % len(news_images)])
    
    # Use first 5 images for the carousel
    news_images = news_images[:5]
    logger.info(f"Using {len(news_images)} news-related images for carousel")

    # 5. Generate Carousel Script
    script = brain.generate_carousel_script(
        best_article, 
        reference_image_path=None,
        use_ai_images=USE_AI_IMAGE_GENERATION
    )
    if not script:
        logger.error("Failed to generate script")
        return
    
    # Save script JSON to json_temp (overwritten each run)
    script_path = JSON_TEMP_DIR / "carousel_script.json"
    with open(script_path, 'w') as f:
        json.dump(script, f, indent=2)
    logger.info(f"Saved script to {script_path}")

    # 6. Generate Carousel Slides
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = CAROUSELS_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated_images = []
    
    if USE_AI_IMAGE_GENERATION:
        # Use AI Image Generation (Vertex AI required)
        logger.info("Using AI Image Generation...")
        ai_gen = AIImageGenerator()
        slides_data = script.get("slides", [])
        
        for i, slide in enumerate(slides_data):
            image_prompt = slide.get("image_prompt", "A modern news background")
            output_filename = f"slide_{i+1}.jpg"
            
            logger.info(f"Generating slide {i+1}/5...")
            
            gen_path = ai_gen.generate_image(
                prompt=image_prompt,
                output_filename=output_filename,
                reference_image_path=str(ref_image_path) if ref_image_path else None
            )
            
            if gen_path:
                import shutil
                final_path = output_dir / output_filename
                shutil.copy(gen_path, final_path)
                generated_images.append(str(final_path))
            else:
                logger.warning(f"Failed to generate slide {i+1}")
    else:
        # Use Pillow for text overlay (Free tier)
        logger.info("Using Pillow for carousel generation...")
        cg = CarouselGenerator(logo_path=BASE_DIR / "assets" / "logo.png")
        
        # Use Tavily news images as backgrounds (one per slide)
        generated_images = cg.create_carousel(
            script=script,
            background_images=news_images,  # Pass array of images
            output_dir=output_dir
        )
    
    # 6. Create ZIP and Email
    if generated_images:
        zip_path = output_dir / "carousel.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img in generated_images:
                zipf.write(img, Path(img).name)
        
        mailer.send_email(
            subject=f"New Carousel: {best_article['title'][:50]}...",
            body=f"Headline: {best_article['title']}\n\nGenerated {len(generated_images)} slides.\n\nScript:\n{json.dumps(script, indent=2)}",
            attachments=[str(zip_path)]
        )
        
        # Log to daily store
        save_news_item({
            "headline": best_article['title'],
            "summary": best_article.get("description"),
            "type": "carousel",
            "slides": len(generated_images)
        })
        
        logger.info(f"✅ Carousel created: {len(generated_images)} slides")
    else:
        logger.error("No images were generated")

def run_daily_digest():
    """Generate daily summary (placeholder for now)"""
    logger.info("Starting Daily Digest Job...")
    
    today_items = get_todays_items()
    if not today_items:
        logger.warning("No news logged today.")
        return
    
    logger.info(f"Today's summary: {len(today_items)} stories processed")
    # TODO: Implement daily video/reel if needed

def main():
    parser = argparse.ArgumentParser(description="AI News Agent")
    parser.add_argument("--mode", choices=["hourly", "digest"], required=True, help="Mode to run")
    parser.add_argument("--test", action="store_true", help="Test mode")
    
    args = parser.parse_args()
    
    if args.mode == "hourly":
        run_hourly_job()
    elif args.mode == "digest":
        run_daily_digest()

if __name__ == "__main__":
    main()
