#!/bin/bash
# Quick setup script for Codebase Genius in WSL

echo "🧠 Codebase Genius - WSL Setup"
echo "================================"

# Check if we're in WSL
if ! grep -qi microsoft /proc/version; then
    echo "⚠️  This script is designed for WSL. Proceeding anyway..."
fi

# Navigate to project directory
cd "$(dirname "$0")"

echo "📁 Current directory: $(pwd)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Test the conversion
echo "🧪 Testing conversion..."
python test_conversion.py

# Check if test passed
if [ $? -eq 0 ]; then
    echo "✅ Conversion test passed!"
    
    # Start the services
    echo "🚀 Starting services..."
    echo "You can now run: python start.py start"
    echo ""
    echo "Or to start just the API:"
    echo "python start.py start api"
    echo ""
    echo "Or to start just the frontend:"
    echo "python start.py start frontend"
    
else
    echo "❌ Conversion test failed. Please check the errors above."
    exit 1
fi
