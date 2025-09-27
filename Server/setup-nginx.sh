#!/bin/bash

# ECHONET API Nginx Setup Script
# This script helps set up nginx configuration for api.echonet.live

echo "🚀 Setting up Nginx for api.echonet.live"

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx is not installed. Installing..."
    sudo apt update
    sudo apt install nginx -y
else
    echo "✅ Nginx is already installed"
fi

# Copy the nginx configuration
echo "📝 Setting up nginx configuration..."
sudo cp nginx.conf /etc/nginx/sites-available/api.echonet.live

# Create symlink to enable the site
sudo ln -sf /etc/nginx/sites-available/api.echonet.live /etc/nginx/sites-enabled/

# Remove default nginx site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # Install certbot for SSL if not already installed
    if ! command -v certbot &> /dev/null; then
        echo "🔒 Installing Certbot for SSL certificates..."
        sudo apt install certbot python3-certbot-nginx -y
    fi
    
    echo "🔒 Setting up SSL certificate with Let's Encrypt..."
    echo "Run this command manually after DNS is configured:"
    echo "sudo certbot --nginx -d api.echonet.live"
    
    # Restart nginx
    echo "🔄 Restarting nginx..."
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    echo ""
    echo "✅ Nginx setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Ensure your DNS A record points api.echonet.live to your server IP (82.177.167.151)"
    echo "2. Run: sudo certbot --nginx -d api.echonet.live"
    echo "3. Start your Node.js application on port 3001"
    echo "4. Test: curl https://api.echonet.live/healthz"
    echo ""
    
else
    echo "❌ Nginx configuration test failed. Please check the configuration."
    exit 1
fi