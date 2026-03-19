"""
AI Image Generator using Gemini 2.5 Flash Image (Nano Banana).
This model supports text rendering in generated images.
"""
from google import genai
from pathlib import Path
from config import GEMINI_API_KEY, IMAGE_TEMP_DIR, get_logger

logger = get_logger("AIImageGenerator")

class AIImageGenerator:
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is missing!")
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        # Initialize the genai client
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_image(self, prompt, output_filename, reference_image_path=None):
        """
        Generates an image using Gemini 2.5 Flash Image.
        
        Args:
            prompt: Text prompt describing the image to generate
            output_filename: Filename to save (will be saved in IMAGE_TEMP_DIR)
            reference_image_path: Optional reference image for style/context
            
        Returns:
            Path to generated image or None if failed
        """
        try:
            logger.info(f"Generating image with Gemini 2.5 Flash Image...")
            logger.debug(f"Prompt: {prompt[:100]}...")
            
            # Save to temp directory
            output_path = IMAGE_TEMP_DIR / output_filename
            
            # Prepare the generation config
            config = {
                'number_of_images': 1,
                'aspect_ratio': '9:16',  # Portrait for Instagram
                'safety_filter_level': 'block_some',
                'person_generation': 'allow_adult'
            }
            
            # Add reference image context to prompt if provided
            if reference_image_path:
                ref_path = Path(reference_image_path)
                if ref_path.exists():
                    logger.info("Using reference image for style context")
                    prompt = f"{prompt}\n\nStyle reference: Use a photorealistic news photography style similar to professional journalism."
            
            # Generate the image using gemini-2.5-flash-image
            response = self.client.models.generate_images(
                model='gemini-2.5-flash-image',  # Nano Banana model
                prompt=prompt,
                config=config
            )
            
            # Save the generated image
            if response.generated_images:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # The response contains the image data
                image_data = response.generated_images[0].image.image_bytes
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                logger.info(f"✅ Image saved to {output_path}")
                return str(output_path)
            else:
                logger.warning("No image data in response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            logger.error(f"This might be due to API quota limits or model availability")
            return None

if __name__ == "__main__":
    # Test
    gen = AIImageGenerator()
    test_prompt = """
    Create a modern Instagram news post cover image.
    Background: A dramatic cityscape at sunset.
    Text: Write 'BREAKING NEWS' in large bold white font at the top.
    Professional journalistic style, portrait format.
    """
    result = gen.generate_image(test_prompt, "test_gen.jpg")
    print(f"Generated: {result}")
