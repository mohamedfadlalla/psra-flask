#!/bin/bash

# ==============================================================================
# PSRA-Flask Update Deployment Script
# 
# Purpose: Pull latest code, update dependencies, and restart Gunicorn
# Run as: flaskapp (e.g., ./update.sh)
# Environment: 1 CPU, 1GB RAM (Oracle Cloud)
# ==============================================================================

# Fail fast on any error
set -eo pipefail

echo "================================================================="
echo " Starting Deployment Update Process - $(date)"
echo "================================================================="

APP_DIR="/home/flaskapp/psra-flask"

# 1. Navigate to project directory
echo "-> Navigating to project directory ($APP_DIR)..."
cd "$APP_DIR" || { echo "Error: Application directory not found."; exit 1; }

# Record current commit before pull
OLD_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "None")
echo "-> Current Git Commit: $OLD_COMMIT"

# 2. Pull latest code
echo "-> Pulling latest code from origin master..."
git pull origin master

# Record new commit after pull
NEW_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "None")
echo "-> New Git Commit: $NEW_COMMIT"

if [ "$OLD_COMMIT" == "$NEW_COMMIT" ]; then
    echo "-> Code is already up to date. Proceeding with service restart just in case."
fi

# 3. Update Python dependencies
echo "-> Checking and installing new dependencies..."
# Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt

# 4. Restart Gunicorn service
echo "-> Restarting Gunicorn service..."
# Use sudo to restart the service (flaskapp user has NOPASSWD access configured in bootstrap.sh)
sudo systemctl restart psra_flask.service

# 5. Check Service Status
echo "-> Verifying Gunicorn status..."
sleep 2 # Give it a moment to restart
if systemctl is-active --quiet psra_flask.service; then
    echo "-> Gunicorn service restarted successfully."
else
    echo "Error: Gunicorn service failed after restart."
    sudo systemctl status psra_flask.service --no-pager
    exit 1
fi

echo "================================================================="
echo " Deployment Update Complete! 🚀"
echo "================================================================="
