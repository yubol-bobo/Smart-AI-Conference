#!/usr/bin/env python3
"""
Generate rating distribution plots for each primary area
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def plot_area_rating_distribution(df, area_name, output_dir='outputs'):
    """
    Create rating distribution plot for a specific area
    """
    # Filter to this area
    area_df = df[df['primary_area'] == area_name].copy()
    rated_df = area_df[area_df['avg_rating'].notna()].copy()
    
    if len(rated_df) == 0:
        print(f"  ⚠ Skipping {area_name}: No ratings")
        return
    
    # Get value counts and sort
    rating_counts = rated_df['avg_rating'].value_counts().sort_index()
    unique_ratings = rating_counts.index.values
    counts = rating_counts.values
    
    # Calculate cumulative percentages
    total = len(rated_df)
    cumsum = np.cumsum(counts)
    cumulative_pct = (cumsum / total) * 100
    
    # Calculate statistics
    mean_rating = rated_df['avg_rating'].mean()
    median_rating = rated_df['avg_rating'].median()
    std_rating = rated_df['avg_rating'].std()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 20))
    
    # Create horizontal bars
    bars = ax.barh(range(len(unique_ratings)), counts, 
                    height=0.8, 
                    edgecolor='black',
                    linewidth=0.5,
                    alpha=0.85)
    
    # Color gradient: blue -> yellow -> green
    colors_list = ['#2166ac', '#4393c3', '#92c5de', '#fef0a5', '#f4e842', '#d7ee5e', '#a6d96a', '#66bd63', '#1a9850']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('rating_colors', colors_list, N=n_bins)
    
    # Normalize ratings to [0, 1] for colormap
    min_rating = unique_ratings.min()
    max_rating = unique_ratings.max()
    
    for i, rating in enumerate(unique_ratings):
        norm_rating = (rating - min_rating) / (max_rating - min_rating) if max_rating > min_rating else 0.5
        bars[i].set_facecolor(cmap(norm_rating))
    
    # Add cumulative percentage labels with count
    max_count = max(counts)
    for i, (count, cum_pct) in enumerate(zip(counts, cumulative_pct)):
        label = f'({count}) {cum_pct:.1f}%'
        
        if count > max_count * 0.05:
            ax.text(count + max_count * 0.01, i, label, 
                   ha='left', va='center', 
                   fontsize=12, fontweight='bold')
        else:
            ax.text(count + max_count * 0.005, i, label, 
                   ha='left', va='center', 
                   fontsize=11, fontweight='bold',
                   color='darkred')
    
    # Set y-axis labels
    ax.set_yticks(range(len(unique_ratings)))
    ax.set_yticklabels([f'{r:.2f}' if r != int(r) else f'{int(r)}' 
                        for r in unique_ratings], 
                       fontsize=14)
    
    # Add horizontal lines for mean and median
    mean_idx = np.searchsorted(unique_ratings, mean_rating)
    median_idx = np.searchsorted(unique_ratings, median_rating)
    
    ax.axhline(mean_idx, color='red', linestyle='--', linewidth=2.5, 
               label=f'Mean: {mean_rating:.2f}', alpha=0.8, zorder=10)
    ax.axhline(median_idx, color='purple', linestyle='--', linewidth=2.5, 
               label=f'Median: {median_rating:.2f}', alpha=0.8, zorder=10)
    
    # Labels and title
    ax.set_ylabel('Average Rating (each bar = unique rating value)', 
                  fontsize=18, fontweight='bold', labelpad=10)
    ax.set_xlabel('Number of Submissions', fontsize=18, fontweight='bold')
    
    # Truncate long area names for title
    display_name = area_name if len(area_name) <= 60 else area_name[:57] + '...'
    ax.set_title(f'Rating Distribution - {display_name}\n' + 
                 f'n = {len(rated_df):,} submissions | Cumulative % shown',
                 fontsize=22, fontweight='bold', pad=20)
    
    # Add statistics box
    stats_text = (
        f'Statistics:\n'
        f'───────────────\n'
        f'Mean:      {mean_rating:.3f}\n'
        f'Median:    {median_rating:.3f}\n'
        f'Std Dev:   {std_rating:.3f}\n'
        f'Min:       {rated_df["avg_rating"].min():.2f}\n'
        f'Max:       {rated_df["avg_rating"].max():.2f}\n'
        f'───────────────\n'
        f'Q1 (25%):  {rated_df["avg_rating"].quantile(0.25):.2f}\n'
        f'Q3 (75%):  {rated_df["avg_rating"].quantile(0.75):.2f}\n'
        f'IQR:       {rated_df["avg_rating"].quantile(0.75) - rated_df["avg_rating"].quantile(0.25):.2f}\n'
        f'───────────────\n'
        f'Unique Values: {len(unique_ratings)}'
    )
    
    ax.text(0.98, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85, edgecolor='black', linewidth=1.5),
            family='monospace',
            zorder=15)
    
    # Add rating scale
    scale_text = (
        'Rating Scale:\n'
        '  2: Strong Reject\n'
        '  4: Reject\n'
        '  5: Marginally Below\n'
        '  6: Weak Accept\n'
        '  8: Accept\n'
        ' 10: Strong Accept'
    )
    
    ax.text(0.98, 0.02, scale_text,
            transform=ax.transAxes,
            fontsize=13,
            verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8, edgecolor='black', linewidth=1.5),
            family='monospace',
            zorder=15)
    
    # Legend
    ax.legend(loc='lower right', fontsize=14, framealpha=0.95, 
              edgecolor='black', fancybox=True, bbox_to_anchor=(1.0, 0.25))
    
    # Adjust tick label size
    ax.tick_params(axis='both', labelsize=14)
    
    # Grid styling
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='x')
    ax.set_axisbelow(True)
    
    # Invert y-axis
    ax.invert_yaxis()
    
    # Tight layout
    plt.tight_layout()
    
    # Save plot - sanitize filename
    safe_name = area_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
    safe_name = safe_name[:100]  # Limit filename length
    output_file = Path(output_dir) / f'rating_dist_{safe_name}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {output_file.name}")
    
    plt.close()


def main(csv_file='data/ratings_data.csv', 
         output_dir='outputs',
         min_submissions=50):
    """
    Generate rating distribution plots for each primary area
    
    Args:
        csv_file: Path to ratings CSV
        output_dir: Directory to save plots
        min_submissions: Minimum number of submissions to generate plot (default: 50)
    """
    print("="*60)
    print("Generating Rating Distribution by Primary Area")
    print("="*60)
    
    # Load data
    df = pd.read_csv(csv_file)
    
    # Filter to submissions with reviews
    df = df[df['avg_rating'].notna()].copy()
    
    print(f"\nLoaded {len(df):,} submissions with ratings")
    
    # Get area counts
    area_counts = df['primary_area'].value_counts()
    
    # Filter areas with minimum submissions
    valid_areas = area_counts[area_counts >= min_submissions].index.tolist()
    
    print(f"Found {len(valid_areas)} areas with ≥{min_submissions} submissions")
    print(f"Generating plots...\n")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate plot for each area
    for i, area in enumerate(valid_areas, 1):
        count = area_counts[area]
        print(f"[{i}/{len(valid_areas)}] {area[:60]}... ({count} submissions)")
        plot_area_rating_distribution(df, area, output_dir)
    
    print("\n" + "="*60)
    print(f"✅ Generated {len(valid_areas)} plots")
    print(f"   Saved to: {output_dir}/")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'data/ratings_data.csv'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'outputs'
    min_subs = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    main(csv_file, output_dir, min_subs)

