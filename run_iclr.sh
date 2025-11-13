#!/bin/bash
# Universal ICLR Analysis Runner
# Simplified wrapper for the complete 3-step workflow
#
# Usage:
#   ./run_iclr.sh 2025              # Past conference with decisions
#   ./run_iclr.sh 2026 no-decisions # Current conference without decisions
#   ./run_iclr.sh 2024              # Another past conference

set -e

# Parse arguments
YEAR=${1}
NO_DECISIONS_FLAG=""
OUTPUT_DIR="iclr_${YEAR}/iclr_${YEAR}_v1"

if [ -z "$YEAR" ]; then
    echo "Usage: $0 <year> [no-decisions]"
    echo ""
    echo "Examples:"
    echo "  $0 2025              # ICLR 2025 with decisions"
    echo "  $0 2026 no-decisions # ICLR 2026 without decisions"
    echo ""
    exit 1
fi

# Check for no-decisions flag
if [[ "$2" == "no-decisions" ]] || [[ "$2" == "--no-decisions" ]]; then
    NO_DECISIONS_FLAG="--no-decisions"
fi

echo "======================================"
echo "ICLR ${YEAR} Analysis Pipeline"
echo "======================================"
echo "Workflow: Metadata → Extraction → Analysis"
echo ""
echo "Configuration:"
echo "  Year: ${YEAR}"
echo "  Output: ${OUTPUT_DIR}"
echo "  Decisions: $([ -z "$NO_DECISIONS_FLAG" ] && echo 'Enabled' || echo 'Disabled (Pending)')"
echo ""
echo "======================================"
echo ""

# Create output directory
mkdir -p "${OUTPUT_DIR}"
mkdir -p "outputs/iclr_${YEAR}"

# STEP 1: Scrape metadata
echo "STEP 1/3: Collecting metadata from OpenReview..."
echo "This may take 30-60 minutes depending on conference size..."
echo ""

if [ -z "$NO_DECISIONS_FLAG" ]; then
    python3 src/scrape_iclr.py \
        --year "${YEAR}" \
        --output "${OUTPUT_DIR}"
else
    python3 src/scrape_iclr.py \
        --year "${YEAR}" \
        --output "${OUTPUT_DIR}" \
        --no-decisions
fi

echo ""
echo "✅ Metadata collection complete!"

# STEP 2: Extract ratings
echo ""
echo "STEP 2/3: Extracting ratings and decisions..."
python3 src/extract_ratings.py "${OUTPUT_DIR}/submissions_metadata.json" "${OUTPUT_DIR}/ratings_data.csv"
echo "✅ Extraction complete!"

# STEP 3: Generate visualizations
echo ""
echo "STEP 3/3: Generating visualizations..."
echo "  → Main rating distribution..."
python3 src/plot_rating_distribution.py --input "${OUTPUT_DIR}/ratings_data.csv" --output "outputs/iclr_${YEAR}" 2>/dev/null || true
echo "  → Area-specific plots..."
python3 src/plot_rating_by_area.py --input "${OUTPUT_DIR}/ratings_data.csv" --output "outputs/iclr_${YEAR}" 2>/dev/null || true
echo "  → Additional analyses..."
python3 src/analyze_distributions.py --input "${OUTPUT_DIR}/ratings_data.csv" --output "outputs/iclr_${YEAR}" 2>/dev/null || true
echo "✅ Visualizations complete!"

echo ""
echo "======================================"
echo "✅ PIPELINE COMPLETE!"
echo "======================================"
echo ""
echo "📁 Results:"
echo "  Data:"
echo "    - Metadata: ${OUTPUT_DIR}/submissions_metadata.json"
echo "    - Ratings:  ${OUTPUT_DIR}/ratings_data.csv"
echo ""
echo "  Visualizations:"
echo "    - Directory: outputs/iclr_${YEAR}/"
ls outputs/iclr_${YEAR}/*.png 2>/dev/null | wc -l | xargs -I {} echo "    - {} plots generated"
echo ""
echo "Next steps:"
echo "  - Review visualizations: open outputs/iclr_${YEAR}/"
echo "  - Check ratings data: cat ${OUTPUT_DIR}/ratings_data.csv | head"
echo ""
echo "  - Processed: ${OUTPUT_DIR}/ratings_data.csv"
echo ""
echo "📊 Next steps:"
echo "  - Generate plots: python src/plot_rating_distribution.py"
echo "  - Area analysis: python src/plot_rating_by_area.py"
echo "  - Full pipeline: ./run_all.sh ${YEAR}$([ -n "$NO_DECISIONS_FLAG" ] && echo ' --no-decisions')"
echo ""
