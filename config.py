import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Subdirectories
FONTS_DIR = ASSETS_DIR / "fonts"
MUSIC_DIR = ASSETS_DIR / "music"
CAROUSELS_DIR = ASSETS_DIR / "carousels"
REELS_DIR = ASSETS_DIR / "reels"

# Temp directories (overwritten each run)
IMAGE_TEMP_DIR = BASE_DIR / "image_temp"
JSON_TEMP_DIR = BASE_DIR / "json_temp"

# Ensure temp directories exist
IMAGE_TEMP_DIR.mkdir(parents=True, exist_ok=True)
JSON_TEMP_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Set GOOGLE_API_KEY for google-generativeai library compatibility
if GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Email Config
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Image Generation Mode
# Set to True to use AI image generation (requires Vertex AI)
# Set to False to use Pillow for text overlay (free tier)
USE_AI_IMAGE_GENERATION = os.getenv("USE_AI_IMAGE_GENERATION", "false").lower() == "true"

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log"),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    return logging.getLogger(name)
