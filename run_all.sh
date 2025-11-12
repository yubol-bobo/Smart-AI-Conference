#!/bin/bash
# Run complete ICLR 2026 analysis pipeline

set -e

echo "======================================"
echo "ICLR 2026 Analysis - Full Pipeline"
echo "======================================"
echo ""

# Check if data directory exists
if [ ! -d "data" ]; then
    mkdir -p data
    echo "Created data directory"
fi

# Check if outputs directory exists
if [ ! -d "outputs" ]; then
    mkdir -p outputs
    echo "Created outputs directory"
fi

echo ""
echo "Step 1/5: Scraping submissions..."
echo "This may take 30-60 minutes..."
python src/scrape_iclr_submissions.py
echo "✅ Scraping complete!"

echo ""
echo "Step 2/5: Extracting ratings..."
python src/extract_ratings_fast.py
echo "✅ Extraction complete!"

echo ""
echo "Step 3/5: Generating main rating distribution..."
python src/plot_rating_distribution.py
echo "✅ Main plot complete!"

echo ""
echo "Step 4/5: Generating area-specific distributions..."
python src/plot_rating_by_area.py
echo "✅ Area plots complete!"

echo ""
echo "Step 5/5: Generating additional analyses..."
python src/analyze_distributions.py
echo "✅ Additional analyses complete!"

echo ""
echo "======================================"
echo "✅ COMPLETE! All analyses finished."
echo "======================================"
echo ""
echo "📊 Results saved in outputs/"
echo "📈 Data saved in data/"
echo ""
echo "Generated files:"
ls -lh outputs/*.png 2>/dev/null | wc -l | xargs echo "  - Visualizations:"
ls -lh data/*.csv data/*.json 2>/dev/null | wc -l | xargs echo "  - Data files:"
echo ""

