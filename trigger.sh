#!/bin/bash

# US Market Trends Trigger Script
PROJECT_DIR="us-market-trends"
VENV_PYTHON=".venv/bin/python"

echo "🚀 Starting US Market Trends Update..."

# 1. Fetch data
echo "Fetching market data..."
$VENV_PYTHON $PROJECT_DIR/scripts/fetch_market_data.py

# 2. Generate dashboard
echo "Generating dashboard..."
$VENV_PYTHON $PROJECT_DIR/scripts/generate_dashboard.py

echo "✅ Dashboard updated successfully! Check $PROJECT_DIR/index.html"
