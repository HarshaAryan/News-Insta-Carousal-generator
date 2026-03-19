import json
import datetime
from config import DATA_DIR, get_logger

logger = get_logger("DailyStore")
LOG_FILE = DATA_DIR / "daily_log.json"

def _load_log():
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
            # Check if log is from today, else reset
            if data and data[0].get("date") != str(datetime.date.today()):
                logger.info("New day detected. Clearing old logs.")
                return []
            return data
    except Exception as e:
        logger.error(f"Error loading daily log: {e}")
        return []

def _save_log(data):
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving daily log: {e}")

def save_news_item(news_item):
    """
    Saves a procesed news item to the daily log.
    news_item dict should contain: headline, summary, type (carousel/reel), timestamp
    """
    log = _load_log()
    news_item["date"] = str(datetime.date.today())
    log.append(news_item)
    _save_log(log)
    logger.info(f"Saved news item: {news_item.get('headline')}")

def get_todays_items():
    return _load_log()

def is_duplicate(headline):
    log = _load_log()
    for item in log:
        if item.get("headline") == headline:
            return True
    return False
