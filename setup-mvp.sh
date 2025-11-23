#!/bin/bash

# MVP Setup Script for ClickBank Affiliate SaaS
# This script helps set up PostgreSQL and Redis for local development

set -e

echo "=================================="
echo "MVP Setup Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo -e "${YELLOW}Warning: Running as root${NC}"
fi

echo "Step 1: Installing PostgreSQL and Redis..."
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}Cannot detect OS${NC}"
    exit 1
fi

# Install based on OS
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    echo "Detected Debian/Ubuntu system"

    # Update package list
    sudo apt-get update

    # Install PostgreSQL
    if ! command -v psql &> /dev/null; then
        echo "Installing PostgreSQL..."
        sudo apt-get install -y postgresql postgresql-contrib
    else
        echo -e "${GREEN}PostgreSQL already installed${NC}"
    fi

    # Install Redis
    if ! command -v redis-cli &> /dev/null; then
        echo "Installing Redis..."
        sudo apt-get install -y redis-server
    else
        echo -e "${GREEN}Redis already installed${NC}"
    fi

    # Start services
    sudo systemctl start postgresql
    sudo systemctl start redis-server
    sudo systemctl enable postgresql
    sudo systemctl enable redis-server

elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
    echo "Detected Red Hat/CentOS/Fedora system"

    # Install PostgreSQL
    if ! command -v psql &> /dev/null; then
        echo "Installing PostgreSQL..."
        sudo dnf install -y postgresql-server postgresql-contrib
        sudo postgresql-setup --initdb
    else
        echo -e "${GREEN}PostgreSQL already installed${NC}"
    fi

    # Install Redis
    if ! command -v redis-cli &> /dev/null; then
        echo "Installing Redis..."
        sudo dnf install -y redis
    else
        echo -e "${GREEN}Redis already installed${NC}"
    fi

    # Start services
    sudo systemctl start postgresql
    sudo systemctl start redis
    sudo systemctl enable postgresql
    sudo systemctl enable redis
else
    echo -e "${RED}Unsupported OS: $OS${NC}"
    echo "Please install PostgreSQL 15+ and Redis 7+ manually"
    exit 1
fi

echo ""
echo "Step 2: Configuring PostgreSQL..."
echo ""

# Create database and user
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'clickbank_saas'" | grep -q 1 || \
sudo -u postgres psql <<EOF
CREATE DATABASE clickbank_saas;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE clickbank_saas TO postgres;
\q
EOF

echo -e "${GREEN}PostgreSQL database 'clickbank_saas' ready${NC}"

echo ""
echo "Step 3: Verifying services..."
echo ""

# Check PostgreSQL
if sudo systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
    psql -U postgres -h localhost -p 5432 -c "SELECT version();" clickbank_saas || echo -e "${YELLOW}Note: May need to configure pg_hba.conf for password auth${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not running${NC}"
fi

# Check Redis
if sudo systemctl is-active --quiet redis-server || sudo systemctl is-active --quiet redis; then
    echo -e "${GREEN}✓ Redis is running${NC}"
    redis-cli ping
else
    echo -e "${RED}✗ Redis is not running${NC}"
fi

echo ""
echo "Step 4: Configure PostgreSQL for password authentication..."
echo ""

# Update pg_hba.conf to allow password authentication
PG_HBA="/etc/postgresql/*/main/pg_hba.conf"
if [ -f $PG_HBA ]; then
    sudo sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' $PG_HBA
    sudo sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/' $PG_HBA
    sudo systemctl restart postgresql
    echo -e "${GREEN}PostgreSQL configured for password authentication${NC}"
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. cd backend"
echo "2. pip install -r requirements.txt"
echo "3. alembic upgrade head"
echo "4. python -m scripts.seed_data"
echo "5. python -m app.main"
echo ""
echo "In another terminal:"
echo "1. cd frontend"
echo "2. npm install"
echo "3. npm run dev"
echo ""
