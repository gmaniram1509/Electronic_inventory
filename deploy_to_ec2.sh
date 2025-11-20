#!/bin/bash
# Deployment script for EC2 instance
# This script sets up the Django application on a fresh EC2 Ubuntu instance

echo "=========================================="
echo "Electronic Inventory - EC2 Deployment"
echo "=========================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11 and dependencies
echo "Installing Python 3.11 and dependencies..."
sudo apt-get install -y python3.11 python3.11-venv python3-pip
sudo apt-get install -y python3.11-dev libpq-dev nginx

# Install PostgreSQL client
echo "Installing PostgreSQL client..."
sudo apt-get install -y postgresql-client

# Create application directory
echo "Setting up application directory..."
sudo mkdir -p /var/www/inventory
sudo chown -R ubuntu:ubuntu /var/www/inventory
cd /var/www/inventory

# Clone or copy project files (you'll need to upload your code here)
echo "Project files should be uploaded to /var/www/inventory/"
echo "You can use SCP or Git to transfer files"

# Create virtual environment
echo "Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env file
echo "Creating .env file..."
echo "You need to manually create /var/www/inventory/.env with your AWS credentials"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser (interactive)
echo "Creating superuser..."
echo "Run: python manage.py createsuperuser"

# Configure Gunicorn
echo "Configuring Gunicorn..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=Gunicorn daemon for Django Inventory App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/inventory/inventory_project
Environment="PATH=/var/www/inventory/venv/bin"
ExecStart=/var/www/inventory/venv/bin/gunicorn \\
          --workers 3 \\
          --bind unix:/var/www/inventory/inventory.sock \\
          inventory_project.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/inventory > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/inventory/inventory_project/staticfiles/;
    }

    location /media/ {
        alias /var/www/inventory/inventory_project/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/inventory/inventory.sock;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx

echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "Next steps:"
echo "1. Create .env file with your AWS credentials"
echo "2. Run migrations: python manage.py migrate"
echo "3. Create superuser: python manage.py createsuperuser"
echo "4. Load sample data: python create_sample_data.py"
echo "5. Access your site at http://your-ec2-public-ip/"
echo "=========================================="
