# Smart AI Conference

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive toolkit for analyzing AI/ML conference submissions using OpenReview data. Extract, analyze, and visualize submission ratings, reviewer confidence, **acceptance decisions**, and research area distributions for any OpenReview-hosted conference.

## 🎯 Features

- **Universal scraper** for any ICLR conference year (past and current)
- **Decision extraction** for past conferences (Oral/Spotlight/Poster/Reject/Withdrawn)
- **Automated data collection** from OpenReview API with intelligent rate limiting
- **Fast extraction** of ratings and metadata (~55,000 submissions/second)
- **Publication-quality visualizations** with customizable color schemes
- **Comprehensive analysis** including acceptance rates and rating thresholds
- **Incremental saves** with checkpoint support for robustness
- **Multi-year comparison** support for trend analysis

## 📊 Completed Analyses

### ICLR 2026 (Current Conference - In Progress)
Successfully analyzed **19,631 submissions** with **74,432 reviews**.

**📁 Visualizations**: [`outputs/iclr_2026/`](./outputs/iclr_2026/) - 26 plots

**Key Statistics:**
- **Average rating**: 4.26 / 10 (median: 4.0)
- **Review coverage**: 99.1% of submissions (19,450 papers)
- **Average reviews per paper**: 3.79
- **Reviewer confidence**: 3.62 / 5 (moderate-high)
- **Decisions**: Not yet posted (conference in progress)

### ICLR 2025 (Past Conference - With Decisions)
Analysis in progress - extracting acceptance decisions (Oral/Spotlight/Poster).

**Expected results:**
- ~10,000-14,000 total submissions
- ~25-30% acceptance rate
- Decision breakdown by research area
- Rating thresholds for acceptance

### 🎨 View Visualizations

**📁 All ICLR 2026 plots**: [`outputs/iclr_2026/`](./outputs/iclr_2026/)

This folder contains **26 publication-quality visualizations**:
- Overall rating distribution with cumulative percentages
- 21 area-specific rating distributions
- Confidence level distributions
- Research area submission counts
- Multi-dimensional analyses

### Key Statistics
- **Average rating**: 4.26 / 10 (median: 4.0)
- **Review coverage**: 99.1% of submissions (19,450 papers)
- **Average reviews per paper**: 3.79
- **Reviewer confidence**: 3.62 / 5 (moderate-high)
- **Top research areas**: 
  - CV/Audio/Language Applications (13.8%)
  - Foundation/Frontier Models & LLMs (13.4%)
  - Alignment/Fairness/Safety (8.6%)

### Featured Plots

Browse [`outputs/iclr_2026/`](./outputs/iclr_2026/) or preview key visualizations:

| Plot | Description |
|------|-------------|
| ![Rating Distribution](./outputs/iclr_2026/average_rating_distribution.png) | **Average Rating Distribution**<br>Shows distribution of 19,450 submissions with cumulative % |
| ![Area Distribution](./outputs/iclr_2026/area_distribution.png) | **Submissions by Research Area**<br>Ranked by submission count across 21 areas |
| ![Confidence](./outputs/iclr_2026/all_confidence_distribution.png) | **Reviewer Confidence Distribution**<br>74,432 individual confidence ratings |

**💡 Note**: Raw data files (26GB) are not included in this repository due to size. The analysis code can regenerate them from OpenReview.

## 🚀 Quick Start

### Explore ICLR 2026 Visualizations (No Setup Required)

Browse the completed analysis visualizations:

```bash
# View the plots
cd outputs/iclr_2026/

# Main visualizations
open average_rating_distribution.png  # Overall distribution
open area_distribution.png           # Submissions by area
open all_confidence_distribution.png  # Reviewer confidence

# Area-specific distributions
ls rating_dist_*.png                 # 21 research area plots
open rating_dist_foundation_or_frontier_models,_including_LLMs.png
```

Or simply browse the [`outputs/iclr_2026/`](./outputs/iclr_2026/) folder on GitHub.

### Run Your Own Analysis

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Conda (recommended) or pip
conda --version
```

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Data_AI

# Automated setup (creates environment and installs dependencies)
./setup.sh

# Or manual setup
conda create -n iclr_analysis python=3.9
conda activate iclr_analysis
pip install -r requirements.txt
```

### Basic Usage

**Complete Workflow:**

```bash
# Activate environment
conda activate iclr_analysis

# STEP 1: Collect metadata from OpenReview (~30-60 minutes)
# For past conference with decisions
python src/scrape_iclr.py --year 2025 --output iclr_2025/iclr_2025_v1

# For current conference without decisions
python src/scrape_iclr.py --year 2026 --output iclr_2026/iclr_2026_v1 --no-decisions

# STEP 2: Extract ratings and decisions (<1 second)
# Automatically detects if decisions are available
python src/extract_ratings.py iclr_2025/iclr_2025_v1/submissions_metadata.json iclr_2025/iclr_2025_v1/ratings_data.csv

# STEP 3: Generate visualizations and analysis
python src/plot_rating_distribution.py iclr_2025/iclr_2025_v1/ratings_data.csv outputs/iclr_2025/
python src/plot_rating_by_area.py iclr_2025/iclr_2025_v1/ratings_data.csv outputs/iclr_2025/
python src/analyze_distributions.py iclr_2025/iclr_2025_v1/ratings_data.csv outputs/iclr_2025/
```

### One-Command Pipeline

```bash
# Run complete analysis pipeline (all 3 steps)
./run_all.sh 2025             # ICLR 2025 with decisions
./run_all.sh 2026 --no-decisions  # ICLR 2026 without decisions
```

## 📁 Project Structure

```
.
├── README.md                         # This file
├── LICENSE                           # MIT License
├── requirements.txt                  # Python dependencies
├── .gitignore                       # Git exclusions
├── setup.sh                         # Environment setup script
├── run_all.sh                       # Complete pipeline script (legacy)
│
├── src/                             # Source code
│   ├── scrape_iclr.py               # ✨ Metadata collection (all years)
│   ├── extract_ratings.py           # ✨ Extract ratings & decisions
│   ├── plot_rating_distribution.py  # Main distribution visualization
│   ├── plot_rating_by_area.py       # Area-specific plots
│   ├── analyze_distributions.py     # Additional distribution analyses
│   ├── test_decision_extraction.py  # Decision extraction tests
│   └── deprecated/                  # Legacy year-specific scripts
│
├── docs/                            # Documentation
│   ├── UNIVERSAL_SCRAPER_GUIDE.md   # Complete usage guide
│   └── UNIVERSAL_SCRAPER_SUMMARY.md # Feature comparison
│
├── outputs/                         # 🎨 Visualizations
│   ├── iclr_2026/                  # ICLR 2026 analysis (26 plots)
│   └── iclr_2025/                  # ICLR 2025 demo plots (6 plots)
│
├── iclr_2026/                       # ICLR 2026 data
│   └── iclr_2026_v1/               # Raw data & processed CSV
│
└── iclr_2025/                       # ICLR 2025 data
    ├── iclr_2025_demo/             # Demo (10 samples)
    ├── iclr_2025_v1/               # Full dataset (in progress)
    ├── ICLR_2025_DEMO_SUMMARY.md   # Demo analysis summary
    └── ICLR_2025_FULL_ANALYSIS_GUIDE.md  # Full analysis guide
```
│       ├── all_confidence_distribution.png
│       ├── all_overall_ratings_distribution.png
│       ├── avg_confidence_distribution.png
│       └── rating_dist_[area].png  # 21 per-area distributions
│
├── data/                            # 📊 Data directory (generated, gitignored)
│   ├── submissions_metadata.json    # Raw scraped data (generated when you run)
│   └── ratings_data.csv            # Processed ratings (generated when you run)
│
└── docs/                           # 📚 Additional documentation
```

**💡 Note**: 
- `outputs/iclr_2026/` contains completed ICLR 2026 visualizations
- Raw data files (26GB) are gitignored - run the scripts to generate them
- New analyses will save data to `data/` and plots to `outputs/`

## 🎯 Key Features

### Universal Scraper
- ✨ **One script for all years** - Past, current, and future conferences
- 🎯 **Smart decision detection** - Automatically extracts Oral/Spotlight/Poster decisions
- ⚡ **Same optimizations** - Batch processing, retry logic, incremental saves
- 📊 **Flexible output** - Works with and without decision data

### Decision Analysis (Past Conferences)
- 🏆 **Accept (Oral)** - Top-tier oral presentations
- ⭐ **Accept (Spotlight)** - Spotlight presentations
- 📄 **Accept (Poster)** - Poster presentations
- ❌ **Reject** - Rejected submissions
- 🚫 **Desk Reject** - Desk rejected without review
- ⬅️ **Withdrawn** - Author-withdrawn submissions

### Rating Analysis (All Conferences)
- 📈 **Comprehensive statistics** - Mean, median, variance, distributions
- 🎨 **Publication-quality plots** - 300 DPI, color-coded gradients
- 🔬 **Multi-dimensional analysis** - By area, decision type, confidence
- 📊 **Acceptance rates** - Calculate thresholds and trends

## 🔧 Configuration

### Universal Scraper (Recommended)

```bash
# Past conference with decisions
python src/scrape_iclr.py --year 2025 --output iclr_2025/iclr_2025_v1

# Current conference without decisions  
python src/scrape_iclr.py --year 2026 --output iclr_2026/v2 --no-decisions

# Custom venue
python src/scrape_iclr.py --venue "ICLR.cc/2024/Conference" --output iclr_2024
```

See [`docs/UNIVERSAL_SCRAPER_GUIDE.md`](./docs/UNIVERSAL_SCRAPER_GUIDE.md) for complete documentation.

### Legacy Configuration

For Different Conferences, modify the `venue_id` in conference-specific scrapers:

```python
# Examples:
venue_id = "ICLR.cc/2026/Conference"       # ICLR 2026
venue_id = "ICLR.cc/2025/Conference"       # ICLR 2025  
venue_id = "NeurIPS.cc/2024/Conference"    # NeurIPS 2024
venue_id = "ICML.cc/2024/Conference"       # ICML 2024
```

### Customization Options

**Color schemes**: Edit `colors_list` in visualization scripts  
**Rate limiting**: Adjust `time.sleep()` values in scraper  
**Minimum submissions**: Change `min_submissions` parameter in area analysis  
**Plot dimensions**: Modify `figsize` in plotting functions

## 📈 Data Fields

### Extracted Information

Each submission includes:
- **Metadata**: Title, abstract, keywords, primary area, submission date
- **Decision**: Oral/Spotlight/Poster/Reject/Withdrawn (for past conferences)
- **Ratings**: Overall (1-10), soundness, presentation, contribution
- **Confidence**: Reviewer confidence levels (1-5)
- **Review text**: Summary, strengths, weaknesses, questions
- **Statistics**: Mean, median, variance, cumulative distributions

### Output Data Structure

**ratings_data.csv** contains:
- `submission_id`: OpenReview submission ID
- `submission_number`: Paper number
- `primary_area`: Research area classification
- **`decision`**: Detailed decision (Accept (Oral/Spotlight/Poster), Reject, Withdrawn, Pending)
- **`decision_type`**: Simplified category (Accept, Reject, Withdrawn, Pending)
- `num_reviews`: Number of reviews received
- `ratings`: List of overall ratings
- `confidences`: List of reviewer confidence scores
- `soundness`, `presentation`, `contribution`: Dimension-specific ratings
- `avg_rating`: Average of all ratings

## 🎨 Visualization Features

All plots include:
- ✨ **Color gradient**: Blue (low) → Yellow (mid) → Green (high)
- 📊 **Detailed labels**: Count, percentage, and cumulative percentage
- 📈 **Statistics boxes**: Mean, median, std dev, quartiles
- 📍 **Reference lines**: Mean and median markers
- 🎯 **Professional styling**: Publication-ready at 300 DPI

### Generated Plots

1. **Average Rating Distribution** - Overall rating distribution with cumulative %
2. **Area-Specific Distributions** - Separate plots for each research area
3. **Confidence Analysis** - Reviewer confidence patterns
4. **Area Submission Counts** - Submissions by research area (ranked)
5. **All Individual Ratings** - Distribution of all individual review ratings

## 🔬 Use Cases

### Research Applications

- **Conference organizers**: Understand submission patterns and reviewer behavior
- **Researchers**: Analyze acceptance thresholds and competitiveness by area
- **Meta-research**: Study peer review processes and rating distributions
- **Trend analysis**: Identify emerging research areas and topics

### Example Analyses

```python
import pandas as pd

# Load processed data
df = pd.read_csv('data/ratings_data.csv')

# High-rated papers
high_rated = df[df['avg_rating'] >= 7.0]
print(f"Papers with rating ≥ 7: {len(high_rated)} ({len(high_rated)/len(df)*100:.1f}%)")

# Most competitive areas
area_stats = df.groupby('primary_area')['avg_rating'].agg(['mean', 'count', 'std'])
most_competitive = area_stats.sort_values('mean')
print("Most competitive areas (lowest avg ratings):")
print(most_competitive.head())

# Reviewer confidence vs rating correlation
import numpy as np
correlation = np.corrcoef(df['avg_rating'].dropna(), df['avg_confidence'].dropna())[0,1]
print(f"Confidence-Rating correlation: {correlation:.3f}")
```

## ⚙️ Advanced Usage

### Batch Processing Multiple Conferences

```bash
# Modify venue_id for each conference, then run:
for venue in "ICLR.cc/2026" "NeurIPS.cc/2024" "ICML.cc/2024"; do
  # Update venue_id in script
  python src/scrape_iclr_submissions.py
  python src/extract_ratings_fast.py
  python src/plot_rating_distribution.py
done
```

### Custom Filtering

```python
# Filter papers by area and rating
df = pd.read_csv('data/ratings_data.csv')

llm_papers = df[df['primary_area'].str.contains('LLM|foundation', case=False)]
high_variance = df[df['num_reviews'] >= 3]
high_variance['rating_std'] = high_variance['ratings'].apply(lambda x: np.std(eval(x)))
controversial = high_variance.nlargest(10, 'rating_std')
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Support for additional conference platforms
- More analysis types (keyword analysis, temporal trends)
- Interactive visualizations
- Automated report generation

Please submit Pull Requests or open Issues for discussion.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenReview** for providing API and data access
- **ICLR, NeurIPS, ICML** and other conferences for open peer review
- The ML research community for open science practices

## 📧 Contact & Support

For questions, suggestions, or bug reports, please open an issue on GitHub.

## 🔗 Related Resources

- [OpenReview API Documentation](https://docs.openreview.net/)
- [ICLR Conference](https://iclr.cc/)
- [NeurIPS Conference](https://neurips.cc/)
- [ICML Conference](https://icml.cc/)

## 📊 Project Status

**Current Version**: Completed ICLR 2026 analysis  
**Next Steps**: Extend to other conferences (NeurIPS, ICML, CVPR)  
**Status**: Production-ready, actively maintained

---

### Citation

If you use this tool in your research, please cite:

```bibtex
@software{ai_conference_analyst,
  title={AI Conference Statistics Analyst},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/Data_AI}
}
```

---

**Last Updated**: November 2024  
**Data Source**: OpenReview API  
**Example Dataset**: ICLR 2026 (19,631 submissions, 74,432 reviews)
