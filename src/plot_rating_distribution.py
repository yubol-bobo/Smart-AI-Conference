#!/usr/bin/env python3
"""
Generate beautiful distribution plots for ICLR 2026 ratings data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def plot_avg_rating_distribution(csv_file='data/ratings_data.csv', 
                                  output_dir='outputs'):
    """
    Create a comprehensive distribution plot for average ratings
    Each unique rating value gets its own bar with cumulative percentage
    """
    # Load data
    df = pd.read_csv(csv_file)
    
    # Filter to submissions with reviews
    rated_df = df[df['avg_rating'].notna()].copy()
    
    print(f"Loaded {len(rated_df):,} submissions with ratings")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get value counts for each unique rating and sort
    rating_counts = rated_df['avg_rating'].value_counts().sort_index()
    unique_ratings = rating_counts.index.values
    counts = rating_counts.values
    
    # Calculate cumulative percentages
    total = len(rated_df)
    cumsum = np.cumsum(counts)
    cumulative_pct = (cumsum / total) * 100
    
    print(f"Number of unique rating values: {len(unique_ratings)}")
    
    # Calculate statistics
    mean_rating = rated_df['avg_rating'].mean()
    median_rating = rated_df['avg_rating'].median()
    std_rating = rated_df['avg_rating'].std()
    
    # Create figure with larger size for horizontal layout
    fig, ax = plt.subplots(figsize=(14, 20))
    
    # Create horizontal bars
    bars = ax.barh(range(len(unique_ratings)), counts, 
                    height=0.8, 
                    edgecolor='black',
                    linewidth=0.5,
                    alpha=0.85)
    
    # Color-code bars with smooth gradient based on rating value
    # Create colormap from blue (low) to yellow (middle) to green (high)
    from matplotlib.colors import LinearSegmentedColormap
    
    # Define color gradient: blue -> cyan -> yellow -> yellow-green -> green
    colors_list = ['#2166ac', '#4393c3', '#92c5de', '#fef0a5', '#f4e842', '#d7ee5e', '#a6d96a', '#66bd63', '#1a9850']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('rating_colors', colors_list, N=n_bins)
    
    # Normalize ratings to [0, 1] for colormap
    min_rating = unique_ratings.min()
    max_rating = unique_ratings.max()
    
    for i, rating in enumerate(unique_ratings):
        # Normalize rating to 0-1 range
        norm_rating = (rating - min_rating) / (max_rating - min_rating)
        bars[i].set_facecolor(cmap(norm_rating))
    
    # Add cumulative percentage labels with count on ALL bars (to the right of bars)
    max_count = max(counts)
    for i, (count, cum_pct) in enumerate(zip(counts, cumulative_pct)):
        # Format: (count) percentage
        label = f'({count}) {cum_pct:.1f}%'
        
        # For long bars, place label to the right; for short bars, also to the right
        if count > max_count * 0.05:  # If bar is >5% of max width
            # Place to right of bar
            ax.text(count + max_count * 0.01, i, label, 
                   ha='left', va='center', 
                   fontsize=12, fontweight='bold')
        else:
            # For very short bars, place label to the right with smaller offset
            ax.text(count + max_count * 0.005, i, label, 
                   ha='left', va='center', 
                   fontsize=11, fontweight='bold',
                   color='darkred')
    
    # Set y-axis labels to show actual rating values (now vertical)
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
    ax.set_title('Distribution of Average Ratings - ICLR 2026\n' + 
                 f'n = {len(rated_df):,} submissions | Cumulative % shown on bars',
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
    
    # Add rating scale reference with color coding - at bottom right
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
    
    # Legend - move to right side, above the rating scale
    ax.legend(loc='lower right', fontsize=14, framealpha=0.95, 
              edgecolor='black', fancybox=True, bbox_to_anchor=(1.0, 0.25))
    
    # Adjust tick label size
    ax.tick_params(axis='both', labelsize=14)
    
    # Grid styling
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='x')
    ax.set_axisbelow(True)
    
    # Invert y-axis so lowest ratings are at bottom
    ax.invert_yaxis()
    
    # Tight layout
    plt.tight_layout()
    
    # Save plot
    output_file = Path(output_dir) / 'average_rating_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_file}")
    
    plt.close()
    
    # Print summary
    print("\n" + "="*60)
    print("RATING DISTRIBUTION SUMMARY")
    print("="*60)
    print(f"Total submissions with ratings: {len(rated_df):,}")
    print(f"Unique rating values: {len(unique_ratings)}")
    print(f"\nCentral Tendency:")
    print(f"  Mean:   {mean_rating:.3f}")
    print(f"  Median: {median_rating:.3f}")
    print(f"  Mode:   {rated_df['avg_rating'].mode().values[0]:.2f}")
    print(f"\nSpread:")
    print(f"  Std Dev: {std_rating:.3f}")
    print(f"  Range:   {rated_df['avg_rating'].min():.2f} - {rated_df['avg_rating'].max():.2f}")
    print(f"  IQR:     {rated_df['avg_rating'].quantile(0.75) - rated_df['avg_rating'].quantile(0.25):.3f}")
    print(f"\nPercentiles:")
    for p in [10, 25, 50, 75, 90]:
        print(f"  {p:2d}th: {rated_df['avg_rating'].quantile(p/100):.2f}")
    
    # Rating categories
    print(f"\nRating Categories:")
    reject = len(rated_df[rated_df['avg_rating'] < 5])
    borderline = len(rated_df[(rated_df['avg_rating'] >= 5) & (rated_df['avg_rating'] < 6)])
    accept = len(rated_df[rated_df['avg_rating'] >= 6])
    
    print(f"  Clear Reject (< 5):        {reject:>5,} ({reject/len(rated_df)*100:>5.1f}%)")
    print(f"  Borderline (5-6):          {borderline:>5,} ({borderline/len(rated_df)*100:>5.1f}%)")
    print(f"  Clear Accept (≥ 6):        {accept:>5,} ({accept/len(rated_df)*100:>5.1f}%)")
    
    # Show top 10 most common rating values
    print(f"\nTop 10 Most Common Rating Values:")
    top_ratings = rating_counts.sort_values(ascending=False).head(10)
    for rating, count in top_ratings.items():
        pct = count / total * 100
        cum_at_rating = cumulative_pct[unique_ratings.tolist().index(rating)]
        print(f"  {rating:>4.2f}: {count:>5,} papers ({pct:>5.1f}%) | Cumulative: {cum_at_rating:>5.1f}%")
    
    print("="*60)


if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'data/ratings_data.csv'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'outputs'
    
    plot_avg_rating_distribution(csv_file, output_dir)
