"""
Carousel Generator using Pillow with the "Tatva" Visual Design System.
Supports easy switching between Pillow and AI image generation.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from pathlib import Path
import requests
from io import BytesIO
from config import FONTS_DIR, IMAGE_TEMP_DIR, get_logger

logger = get_logger("CarouselGenerator")

# Canvas dimensions (Instagram Portrait 4:5)
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350
SAFE_PADDING = 50
LOGO_SIZE = 120
LOGO_PADDING = 50

# Typography
FONT_COVER = 85
FONT_CONTENT = 50
FONT_CTA = 65
TEXT_COLOR = (255, 255, 255)  # Pure white

# Gradient settings
GRADIENT_START_Y = 1350  # Bottom
GRADIENT_END_Y = 800     # 60% mark

class CarouselGenerator:
    def __init__(self, logo_path=None):
        """
        Initialize the carousel generator.
        
        Args:
            logo_path: Path to logo PNG file (optional)
        """
        self.logo = None
        if logo_path and Path(logo_path).exists():
            try:
                self.logo = Image.open(logo_path).convert("RGBA")
                # Resize logo to standard size
                self.logo.thumbnail((LOGO_SIZE, LOGO_SIZE), Image.Resampling.LANCZOS)
                logger.info(f"Loaded logo: {logo_path}")
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
        
        # Try to load Montserrat Bold font
        self.font_cover = self._load_font(FONT_COVER)
        self.font_content = self._load_font(FONT_CONTENT)
        self.font_cta = self._load_font(FONT_CTA)
    
    def _load_font(self, size):
        """Load Montserrat Bold or fallback to default"""
        font_paths = [
            FONTS_DIR / "Montserrat-Bold.ttf",
            FONTS_DIR / "Inter-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",  # Mac fallback
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux fallback
        ]
        
        for font_path in font_paths:
            try:
                if Path(font_path).exists():
                    return ImageFont.truetype(str(font_path), size)
            except:
                continue
        
        # Ultimate fallback
        logger.warning(f"Using default font for size {size}")
        return ImageFont.load_default()
    
    def _download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGB")
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None
    
    def _create_gradient_overlay(self):
        """Create a black gradient overlay (bottom to 60% mark)"""
        # Create a gradient mask
        gradient = Image.new('L', (CANVAS_WIDTH, CANVAS_HEIGHT), 0)
        draw = ImageDraw.Draw(gradient)
        
        # Draw gradient from bottom (255 opacity) to 60% mark (0 opacity)
        for y in range(GRADIENT_END_Y, GRADIENT_START_Y):
            # Calculate alpha: 255 at bottom, 0 at top
            alpha = int(255 * (y - GRADIENT_END_Y) / (GRADIENT_START_Y - GRADIENT_END_Y))
            draw.rectangle([(0, y), (CANVAS_WIDTH, y + 1)], fill=alpha)
        
        # Create black overlay with gradient alpha
        overlay = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
        overlay.putalpha(gradient)
        
        return overlay
    
    def create_slide(self, background_image_url, headline_text, slide_type="content", apply_blur=False):
        """
        Create a single slide with the Tatva visual stack.
        
        Args:
            background_image_url: URL or path to background image
            headline_text: Text to display
            slide_type: "cover", "content", or "cta"
            apply_blur: Apply Gaussian blur to busy backgrounds
            
        Returns:
            PIL Image object
        """
        # Create canvas
        canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0))
        
        # Layer 1: Background Image
        if slide_type != "cta":
            # Download or load image
            if background_image_url.startswith('http'):
                bg_image = self._download_image(background_image_url)
            else:
                bg_image = Image.open(background_image_url).convert("RGB")
            
            if bg_image:
                # Resize to cover canvas (center crop)
                bg_image = ImageOps.fit(bg_image, (CANVAS_WIDTH, CANVAS_HEIGHT), 
                                       Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                
                # Apply blur if requested
                if apply_blur:
                    bg_image = bg_image.filter(ImageFilter.GaussianBlur(5))
                
                canvas.paste(bg_image, (0, 0))
        else:
            # CTA slide: solid brand color (Deep Navy)
            canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), (15, 23, 42))
        
        # Layer 2: Gradient Overlay
        gradient_overlay = self._create_gradient_overlay()
        canvas.paste(gradient_overlay, (0, 0), gradient_overlay)
        
        # Layer 3: Typography
        draw = ImageDraw.Draw(canvas)
        
        # Select font based on slide type
        if slide_type == "cover":
            font = self.font_cover
            text_y = 950
        elif slide_type == "cta":
            font = self.font_cta
            text_y = CANVAS_HEIGHT // 2 - 50  # Centered
        else:  # content
            font = self.font_content
            text_y = 1000
        
        # Word wrap text to fit within safe zone
        max_width = CANVAS_WIDTH - (2 * SAFE_PADDING)
        wrapped_text = self._wrap_text(headline_text, font, max_width)
        
        # Draw text
        text_x = SAFE_PADDING + 10
        for line in wrapped_text:
            draw.text((text_x, text_y), line, font=font, fill=TEXT_COLOR)
            text_y += font.size + 10
        
        # Layer 4: Logo (top-right corner)
        if self.logo and slide_type != "cta":
            logo_x = CANVAS_WIDTH - LOGO_SIZE - LOGO_PADDING
            logo_y = LOGO_PADDING
            canvas.paste(self.logo, (logo_x, logo_y), self.logo)
        
        return canvas
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_carousel(self, script, background_images, output_dir):
        """
        Create a full 5-slide carousel.
        
        Args:
            script: Carousel script from AI Brain (dict with 'slides' key)
            background_images: List of image URLs (one per slide) or single URL
            output_dir: Directory to save slides
            
        Returns:
            List of paths to generated slides
        """
        slides_data = script.get("slides", [])
        generated_slides = []
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle both single URL (legacy) and array of URLs
        if isinstance(background_images, str):
            background_images = [background_images] * len(slides_data)
        
        # Ensure we have enough images (pad with last image if needed)
        while len(background_images) < len(slides_data):
            background_images.append(background_images[-1])
        
        for i, slide_data in enumerate(slides_data):
            slide_num = slide_data.get("slide_number", i + 1)
            text = slide_data.get("text", "")
            
            # Determine slide type
            if slide_num == 1:
                slide_type = "cover"
            elif slide_num == 5:
                slide_type = "cta"
            else:
                slide_type = "content"
            
            # Apply blur for busy content slides
            apply_blur = (slide_type == "content" and i > 1)
            
            # Get the specific background image for this slide
            background_url = background_images[i] if i < len(background_images) else background_images[0]
            
            logger.info(f"Creating slide {slide_num}/5 ({slide_type}) with news image {i+1}...")
            
            # Create slide
            slide_image = self.create_slide(
                background_image_url=background_url,
                headline_text=text,
                slide_type=slide_type,
                apply_blur=apply_blur
            )
            
            # Save slide
            output_path = output_dir / f"slide_{slide_num}.jpg"
            slide_image.save(output_path, "JPEG", quality=95)
            generated_slides.append(str(output_path))
            logger.info(f"✅ Saved: {output_path}")
        
        return generated_slides

if __name__ == "__main__":
    # Test
    cg = CarouselGenerator()
    test_script = {
        "slides": [
            {"slide_number": 1, "text": "BREAKING: Major Tech Announcement Shakes Industry"},
            {"slide_number": 2, "text": "Key Detail: New AI Model Released"},
            {"slide_number": 3, "text": "Impact: Changes Everything We Know"},
            {"slide_number": 4, "text": "Why It Matters: Future of Technology"},
            {"slide_number": 5, "text": "Follow for Daily Tech News"}
        ]
    }
    
    # Use a test image
    test_image = "https://images.unsplash.com/photo-1451187580459-43490279c0fa"
    slides = cg.create_carousel(test_script, test_image, "test_output")
    print(f"Generated {len(slides)} slides")
