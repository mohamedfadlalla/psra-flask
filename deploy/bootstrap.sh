#!/bin/bash

# ==============================================================================
# PSRA-Flask Bootstrap Script
# 
# Purpose: Initialize a fresh Ubuntu server for the Flask application.
# Run as: root (e.g., sudo ./bootstrap.sh)
# Environment: 1 CPU, 1GB RAM (Oracle Cloud)
# Database: SQLite
# ==============================================================================

# Fail fast on any error
set -eo pipefail

echo "================================================================="
echo " Starting Bootstrap Process for PSRA-Flask"
echo "================================================================="

# 1. Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Error: Please run as root (use sudo)"
  exit 1
fi

# 2. Get the server IP address
SERVER_IP=$(curl -s http://checkip.amazonaws.com || wget -qO- http://checkip.amazonaws.com)
if [ -z "$SERVER_IP" ]; then
    echo "Error: Could not determine server public IP."
    exit 1
fi
echo "Server Public IP detected: $SERVER_IP"

# 3. System Update and Dependencies Installation
echo "-> Updating system packages..."
apt-get update -y
# Optional: apt-get upgrade -y (commented out to save time during initial bootstrap if prefered, but recommended)
apt-get upgrade -y

echo "-> Installing required system packages (Git, Python3, Nginx, etc.)..."
apt-get install -y git python3 python3-venv python3-pip build-essential nginx sqlite3 ufw curl

# 4. Configure Firewall (UFW)
echo "-> Configuring UFW Firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
# Enable UFW non-interactively
ufw --force enable

# 5. Create Dedicated Application User
APP_USER="flaskapp"
APP_DIR="/home/$APP_USER/psra-flask"

echo "-> Creating dedicated user: $APP_USER"
if id "$APP_USER" &>/dev/null; then
    echo "User $APP_USER already exists."
else
    useradd -m -s /bin/bash "$APP_USER"
fi

# 6. Clone the Repository
echo "-> Cloning repository..."
if [ -d "$APP_DIR" ]; then
    echo "Directory $APP_DIR already exists. Skipping clone."
else
    # Clone as the flaskapp user
    sudo -u "$APP_USER" git clone https://github.com/mohamedfadlalla/psra-flask.git "$APP_DIR"
fi

# 7. Setup Python Virtual Environment and Install Dependencies
echo "-> Setting up Python virtual environment and dependencies..."
sudo -u "$APP_USER" bash -c "
    cd $APP_DIR
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn  # Ensure gunicorn is explicitly installed just in case
"

# 8. Set up Gunicorn Systemd Service
echo "-> Configuring Gunicorn systemd service..."
SERVICE_FILE="/etc/systemd/system/psra_flask.service"

cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Gunicorn instance to serve PSRA-Flask
After=network.target

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
# Loading .env variables automatically (requires python-dotenv in app, or EnvironmentFile if preferred)
# Since we have 1GB RAM, using 2 workers and 2 threads to be conservative.
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 2 --threads 2 --bind 127.0.0.1:8000 --access-logfile - --error-logfile - app:app
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

echo "-> Reloading systemd and enabling Gunicorn service..."
systemctl daemon-reload
systemctl enable psra_flask.service
systemctl start psra_flask.service

# Check Gunicorn Status
if systemctl is-active --quiet psra_flask.service; then
    echo "Gunicorn service started successfully."
else
    echo "Error: Gunicorn service failed to start."
    systemctl status psra_flask.service --no-pager
    exit 1
fi

# 9. Grant the flaskapp user sudo access JUST for restarting the Gunicorn service (needed for update.sh)
echo "-> Configuring sudoers for deployment script..."
echo "$APP_USER ALL=(ALL) NOPASSWD: /bin/systemctl restart psra_flask.service" > "/etc/sudoers.d/$APP_USER"
chmod 0440 "/etc/sudoers.d/$APP_USER"

# 10. Configure Nginx
echo "-> Configuring Nginx..."
NGINX_CONF="/etc/nginx/sites-available/psra_flask"

cat <<EOF > "$NGINX_CONF"
server {
    listen 80;
    server_name $SERVER_IP; # Use IP for now as DNS is not configured

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for longer requests if needed
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }

    # Optional: Handle static files directly with Nginx
    # location /static {
    #     alias $APP_DIR/static;
    # }
}
EOF

# Enable the site and remove default
ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/"
rm -f /etc/nginx/sites-enabled/default

# Validate Nginx config
if nginx -t; then
    echo "Nginx configuration is valid."
    systemctl restart nginx
    systemctl enable nginx
else
    echo "Error: Nginx configuration is invalid."
    exit 1
fi

# 11. Final Instructions
echo "================================================================="
echo " Bootstrap Complete! 🚀"
echo "================================================================="
echo ""
echo "The application should now be running at: http://$SERVER_IP"
echo ""
echo "Next Steps:"
echo "1. Upload your .env file to $APP_DIR/.env"
echo "2. Restart Gunicorn to apply environment variables:"
echo "   sudo systemctl restart psra_flask.service"
echo ""
echo "Note: Do not run the application as root. Use the update.sh script to deploy future changes."
echo "================================================================="
