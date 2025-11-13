#!/bin/bash
# Run complete ICLR analysis pipeline
# 
# Usage:
#   ./run_all.sh 2025          # ICLR 2025 with decisions
#   ./run_all.sh 2026 --no-decisions  # ICLR 2026 without decisions
#   ./run_all.sh               # Default: ICLR 2026 (legacy mode)

set -e

YEAR=${1:-2026}
NO_DECISIONS=""
OUTPUT_DIR="iclr_${YEAR}/iclr_${YEAR}_v1"

# Check for --no-decisions flag
if [[ "$2" == "--no-decisions" ]] || [[ "$YEAR" == "2026" ]]; then
    NO_DECISIONS="--no-decisions"
fi

echo "======================================"
echo "ICLR ${YEAR} Analysis - Full Pipeline"
echo "======================================"
echo "Workflow: Metadata → Extraction → Analysis"
echo ""

# Create output directories
mkdir -p "${OUTPUT_DIR}"
mkdir -p "outputs/iclr_${YEAR}"
echo "✓ Created output directories"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1/3: Collect Metadata from OpenReview"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "This may take 30-60 minutes..."
if [ -n "$NO_DECISIONS" ]; then
    echo "Mode: Current conference (no decisions)"
    python src/scrape_iclr.py --year "${YEAR}" --output "${OUTPUT_DIR}" ${NO_DECISIONS}
else
    echo "Mode: Past conference (with decisions)"
    python src/scrape_iclr.py --year "${YEAR}" --output "${OUTPUT_DIR}"
fi
echo "✅ Metadata collection complete!"
echo "   Output: ${OUTPUT_DIR}/submissions_metadata.json"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2/3: Extract Ratings and Decisions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Processing submissions metadata..."
python src/extract_ratings.py "${OUTPUT_DIR}/submissions_metadata.json" "${OUTPUT_DIR}/ratings_data.csv"
echo "✅ Extraction complete!"
echo "   Output: ${OUTPUT_DIR}/ratings_data.csv"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3/3: Generate Visualizations and Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "  → Generating main rating distribution..."
echo "  → Generating main rating distribution..."
python src/plot_rating_distribution.py --input "${OUTPUT_DIR}/ratings_data.csv" --output "outputs/iclr_${YEAR}" 2>/dev/null || \
    python src/plot_rating_distribution.py  # Fallback to default paths
echo "  ✓ Main plot complete!"

echo ""
echo "  → Generating area-specific distributions..."
python src/plot_rating_by_area.py --input "${OUTPUT_DIR}/ratings_data.csv" --output "outputs/iclr_${YEAR}" 2>/dev/null || \
    python src/plot_rating_by_area.py  # Fallback to default paths
echo "  ✓ Area plots complete!"

echo ""
echo "  → Generating additional analyses..."
python src/analyze_distributions.py --input "${OUTPUT_DIR}/ratings_data.csv" --output "outputs/iclr_${YEAR}" 2>/dev/null || \
    python src/analyze_distributions.py  # Fallback to default paths
echo "  ✓ Additional analyses complete!"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PIPELINE COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Results saved in outputs/iclr_${YEAR}/"
echo "📈 Data saved in ${OUTPUT_DIR}/"
echo ""
echo "Generated files:"
ls -lh "outputs/iclr_${YEAR}"/*.png 2>/dev/null | wc -l | xargs echo "  - Visualizations:"
ls -lh "${OUTPUT_DIR}"/*.csv "${OUTPUT_DIR}"/*.json 2>/dev/null | wc -l | xargs echo "  - Data files:"
echo ""

