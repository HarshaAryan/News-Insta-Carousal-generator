#!/usr/bin/env python3
"""
Scheduler script for automating the AI News Agent.
Can be run via cron or manually for testing.
"""
import schedule
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Get the project directory
PROJECT_DIR = Path(__file__).parent

def run_hourly_job():
    """Execute the hourly carousel generation"""
    print(f"[{datetime.now()}] Running hourly job...")
    try:
        result = subprocess.run(
            [sys.executable, "main.py", "--mode", "hourly"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Hourly job completed successfully")
        else:
            print(f"❌ Hourly job failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running hourly job: {e}")

def run_daily_digest():
    """Execute the daily digest"""
    print(f"[{datetime.now()}] Running daily digest...")
    try:
        result = subprocess.run(
            [sys.executable, "main.py", "--mode", "digest"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Daily digest completed successfully")
        else:
            print(f"❌ Daily digest failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running daily digest: {e}")

def main():
    print("🤖 AI News Agent Scheduler Started")
    print("=" * 50)
    
    # Schedule hourly job (every 2 hours as per original spec)
    schedule.every(2).hours.do(run_hourly_job)
    
    # Schedule daily digest at 8:00 PM
    schedule.every().day.at("20:00").do(run_daily_digest)
    
    print("📅 Schedule:")
    print("  - Carousel: Every 2 hours")
    print("  - Daily Digest: 8:00 PM")
    print("=" * 50)
    
    # Run once immediately for testing
    print("\n🚀 Running initial job...")
    run_hourly_job()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
