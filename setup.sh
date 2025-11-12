#!/bin/bash
# Setup script for ICLR 2026 Analysis

set -e

echo "======================================"
echo "ICLR 2026 Analysis - Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if conda is available
if command -v conda &> /dev/null; then
    echo ""
    echo "Conda detected. Creating environment..."
    echo "Environment name: iclr_analysis"
    
    # Create conda environment
    conda create -n iclr_analysis python=3.9 -y
    
    echo ""
    echo "Activating environment..."
    eval "$(conda shell.bash hook)"
    conda activate iclr_analysis
    
    # Install requirements
    echo ""
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To activate the environment, run:"
    echo "  conda activate iclr_analysis"
    
else
    echo ""
    echo "Conda not found. Using pip..."
    echo "Consider using a virtual environment."
    echo ""
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install requirements
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To activate the environment, run:"
    echo "  source venv/bin/activate"
fi

echo ""
echo "Next steps:"
echo "  1. Activate the environment (see above)"
echo "  2. Run: python src/scrape_iclr_submissions.py"
echo "  3. Run: python src/extract_ratings_fast.py"
echo "  4. Run: python src/plot_rating_distribution.py"
echo ""

