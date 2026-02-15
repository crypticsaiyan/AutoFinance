#!/usr/bin/env fish

# AutoFinance CLI - Installation Script

echo "🚀 Installing AutoFinance CLI..."
echo ""

# Check Python version
set python_version (python3 --version 2>&1 | cut -d' ' -f2)
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if not test -d venv
    echo ""
    echo "📁 Creating virtual environment..."
    python3 -m venv venv
    
    if test $status -ne 0
        echo "❌ Failed to create virtual environment!"
        exit 1
    end
end

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate.fish

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if test $status -eq 0
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "To run the CLI:"
    echo "  source venv/bin/activate.fish"
    echo "  python main.py"
    echo ""
    echo "Or use the launcher:"
    echo "  ./run.fish"
else
    echo ""
    echo "❌ Installation failed!"
    exit 1
end
