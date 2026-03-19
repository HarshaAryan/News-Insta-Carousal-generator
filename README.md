# AI News Agent - Rebuild with Tavily & Gemini

## Overview
Automated news carousel generation using:
- **Tavily**: News fetching + reference images
- **Gemini 2.0 Flash**: Text analysis & script generation
- **Imagen 3**: AI-generated slides with text rendering

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with:
```
TAVILY_API_KEY=your_tavily_key_here
GEMINI_API_KEY=your_gemini_key_here
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=recipient@gmail.com
```

**Get API Keys:**
- Tavily: https://tavily.com/
- Gemini: https://aistudio.google.com/apikey

### 3. Test Image Generation
```bash
python test_gen.py
```

This will test if Imagen 3 can render text in images.

## Usage

### Generate Single Carousel
```bash
python main.py --mode hourly
```

### Run Automated Scheduler
```bash
python src/scheduler.py
```

This will:
- Generate carousel every 2 hours
- Send daily digest at 8:00 PM
- Email results automatically

## Project Structure
```
├── src/
│   ├── news_fetcher.py      # Tavily integration
│   ├── ai_brain.py           # Gemini analysis & scripting
│   ├── ai_image_gen.py       # Imagen 3 generation
│   ├── scheduler.py          # Automation
│   ├── mailer.py             # Email delivery
│   └── daily_store.py        # Data persistence
├── main.py                   # Main orchestrator
├── test_gen.py              # Test script
└── requirements.txt
```

## Workflow
1. **Fetch**: Tavily searches for breaking news + images
2. **Analyze**: Gemini ranks stories by virality
3. **Script**: Gemini creates 5-slide carousel script
4. **Generate**: Imagen 3 creates slides with text overlay
5. **Deliver**: Zip and email the carousel

## Notes
- Uses **Imagen 3** for text rendering (no Pillow needed)
- Free tier friendly (Gemini + Tavily free tiers)
- Portrait format (9:16) optimized for Instagram
- Automatic error handling and logging
