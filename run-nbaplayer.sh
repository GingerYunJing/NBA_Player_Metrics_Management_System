#!/bin/bash

# NBA Player Metrics Management System - Run Script
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Function to print minimal output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    print_error "Python not found. Install Python 3.7+"
    exit 1
fi

# Check MySQL
if ! command -v mysql >/dev/null 2>&1; then
    print_error "MySQL not found. Install MySQL"
    exit 1
fi

# Check requirements.txt
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    exit 1
fi

# Install dependencies
print_info "Installing dependencies..."
if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt
elif command -v pip >/dev/null 2>&1; then
    pip install -r requirements.txt
else
    print_error "pip not found"
    exit 1
fi


# Get MySQL password
if [ -z "$MYSQL_PASSWORD" ]; then
    echo -n "Enter MySQL root password: "
    read -s MYSQL_PASSWORD
    echo
fi

# Check if databases exist before setting up
print_info "Checking database status..."
print_info "Checking nba_0 database..."
if mysql -u root -p"$MYSQL_PASSWORD" -e "USE nba_0;" 2>/dev/null; then
    print_info "nba_0 database exists"
else
    print_info "nba_0 database missing"
fi

print_info "Checking nba_1 database..."
if mysql -u root -p"$MYSQL_PASSWORD" -e "USE nba_1;" 2>/dev/null; then
    print_info "nba_1 database exists"
else
    print_info "nba_1 database missing"
fi

# Check if both databases exist
if mysql -u root -p"$MYSQL_PASSWORD" -e "USE nba_0;" 2>/dev/null && mysql -u root -p"$MYSQL_PASSWORD" -e "USE nba_1;" 2>/dev/null; then
    print_info "Both databases exist, skipping setup..."
else
    print_info "Setting up missing databases..."
    $PYTHON_CMD insert_initial_data.py "$MYSQL_PASSWORD"
fi

# Run application
print_info "Starting application at http://localhost:5000"
$PYTHON_CMD app.py "$MYSQL_PASSWORD"
