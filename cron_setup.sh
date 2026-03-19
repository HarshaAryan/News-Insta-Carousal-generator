#!/bin/bash

# Get current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)

echo "Setting up Cron Jobs for AI News Agent..."
echo "Project Directory: $DIR"
echo "Python Path: $PYTHON_PATH"

# Cron entries
# 1. Hourly job (Every 2 hours between 8am and 10pm)
HOURLY_JOB="0 8-22/2 * * * cd $DIR && $PYTHON_PATH main.py --mode hourly >> $DIR/logs/cron_hourly.log 2>&1"

# 2. Daily Digest (At 11 PM)
DIGEST_JOB="0 23 * * * cd $DIR && $PYTHON_PATH main.py --mode digest >> $DIR/logs/cron_digest.log 2>&1"

echo ""
echo "Please add the following lines to your crontab (run 'crontab -e'):"
echo "-------------------------------------------------------"
echo "$HOURLY_JOB"
echo "$DIGEST_JOB"
echo "-------------------------------------------------------"
