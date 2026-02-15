#!/usr/bin/env sh

# AutoFinance CLI - Installation Script

echo "🚀 Installing AutoFinance CLI..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d venv ]; then
    echo ""
    echo "📁 Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment!"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
. venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "To run the CLI:"
    echo "  . venv/bin/activate"
    echo "  python main.py"
    echo ""
    echo "Or use the launcher:"
    echo "  ./run.sh"
else
    echo ""
    echo "❌ Installation failed!"
    exit 1
fi
