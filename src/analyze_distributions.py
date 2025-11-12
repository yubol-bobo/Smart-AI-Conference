#!/usr/bin/env python3
"""
Generate distribution analyses and plots
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import ast

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def plot_primary_area_distribution(df, output_dir='outputs'):
    """
    Plot primary area count distribution (ranked most to least)
    """
    area_counts = df['primary_area'].value_counts()
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Create horizontal bars
    bars = ax.barh(range(len(area_counts)), area_counts.values,
                    color='steelblue', edgecolor='black', linewidth=0.5, alpha=0.85)
    
    # Add count labels
    for i, (count, area) in enumerate(zip(area_counts.values, area_counts.index)):
        pct = (count / len(df)) * 100
        ax.text(count + max(area_counts) * 0.01, i, f'{count:,} ({pct:.1f}%)',
               ha='left', va='center', fontsize=11, fontweight='bold')
    
    # Labels
    ax.set_yticks(range(len(area_counts)))
    ax.set_yticklabels(area_counts.index, fontsize=12)
    ax.set_xlabel('Number of Submissions', fontsize=16, fontweight='bold')
    ax.set_ylabel('Primary Research Area', fontsize=16, fontweight='bold')
    ax.set_title('ICLR 2026: Submissions by Primary Research Area\n(Ranked by Count)',
                fontsize=18, fontweight='bold', pad=20)
    
    ax.tick_params(labelsize=12)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='x')
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'area_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()
    
    return area_counts


def plot_all_confidence_ratings(df, output_dir='outputs'):
    """
    Plot distribution of ALL individual confidence ratings
    """
    # Parse all confidence ratings
    all_confidences = []
    for conf_str in df['confidences']:
        try:
            confs = ast.literal_eval(conf_str)
            for c in confs:
                # Extract numeric value
                if isinstance(c, (int, float)):
                    all_confidences.append(c)
                elif isinstance(c, str):
                    try:
                        all_confidences.append(int(c.split(':')[0]))
                    except:
                        pass
        except:
            pass
    
    all_confidences = np.array(all_confidences)
    
    # Get counts for each unique value
    unique_vals, counts = np.unique(all_confidences, return_counts=True)
    total = len(all_confidences)
    cumsum = np.cumsum(counts)
    cumulative_pct = (cumsum / total) * 100
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create bars
    bars = ax.bar(range(len(unique_vals)), counts, 
                   color='coral', edgecolor='black', linewidth=0.5, alpha=0.85)
    
    # Add labels
    for i, (val, count, cum_pct) in enumerate(zip(unique_vals, counts, cumulative_pct)):
        pct = (count / total) * 100
        ax.text(i, count + max(counts) * 0.01, 
               f'{count:,}\n({pct:.1f}%)\n[{cum_pct:.1f}%]',
               ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Labels
    ax.set_xticks(range(len(unique_vals)))
    ax.set_xticklabels([int(v) for v in unique_vals], fontsize=14)
    ax.set_xlabel('Confidence Rating', fontsize=18, fontweight='bold')
    ax.set_ylabel('Number of Individual Ratings', fontsize=18, fontweight='bold')
    ax.set_title('Distribution of All Individual Confidence Ratings\n' +
                f'Total: {total:,} ratings | Labels: (count) [cumulative %]',
                fontsize=20, fontweight='bold', pad=20)
    
    # Add statistics
    stats_text = (
        f'Statistics:\n'
        f'─────────────\n'
        f'Mean:    {all_confidences.mean():.2f}\n'
        f'Median:  {np.median(all_confidences):.0f}\n'
        f'Std Dev: {all_confidences.std():.2f}\n'
        f'Mode:    {unique_vals[counts.argmax()]:.0f}'
    )
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
           fontsize=13, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85, edgecolor='black', linewidth=1.5),
           family='monospace', zorder=15)
    
    ax.tick_params(labelsize=14)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'all_confidence_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def plot_all_overall_ratings(df, output_dir='outputs'):
    """
    Plot distribution of ALL individual overall ratings
    """
    # Parse all overall ratings
    all_ratings = []
    for rating_str in df['ratings']:
        try:
            ratings = ast.literal_eval(rating_str)
            for r in ratings:
                # Extract numeric value
                if isinstance(r, (int, float)):
                    all_ratings.append(r)
                elif isinstance(r, str):
                    try:
                        all_ratings.append(int(r.split(':')[0]))
                    except:
                        pass
        except:
            pass
    
    all_ratings = np.array(all_ratings)
    
    # Get counts for each unique value
    unique_vals, counts = np.unique(all_ratings, return_counts=True)
    total = len(all_ratings)
    cumsum = np.cumsum(counts)
    cumulative_pct = (cumsum / total) * 100
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create bars with color gradient
    from matplotlib.colors import LinearSegmentedColormap
    colors_list = ['#2166ac', '#4393c3', '#92c5de', '#fef0a5', '#f4e842', '#d7ee5e', '#a6d96a', '#66bd63', '#1a9850']
    cmap = LinearSegmentedColormap.from_list('rating_colors', colors_list, N=100)
    
    min_rating = unique_vals.min()
    max_rating = unique_vals.max()
    
    bars = ax.bar(range(len(unique_vals)), counts, 
                   edgecolor='black', linewidth=0.5, alpha=0.85)
    
    for i, (rating, bar) in enumerate(zip(unique_vals, bars)):
        norm_rating = (rating - min_rating) / (max_rating - min_rating) if max_rating > min_rating else 0.5
        bar.set_facecolor(cmap(norm_rating))
    
    # Add labels
    for i, (val, count, cum_pct) in enumerate(zip(unique_vals, counts, cumulative_pct)):
        pct = (count / total) * 100
        ax.text(i, count + max(counts) * 0.01, 
               f'{count:,}\n({pct:.1f}%)\n[{cum_pct:.1f}%]',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Labels
    ax.set_xticks(range(len(unique_vals)))
    ax.set_xticklabels([int(v) if v == int(v) else f'{v:.1f}' for v in unique_vals], 
                       fontsize=12, rotation=45, ha='right')
    ax.set_xlabel('Overall Rating', fontsize=18, fontweight='bold')
    ax.set_ylabel('Number of Individual Ratings', fontsize=18, fontweight='bold')
    ax.set_title('Distribution of All Individual Overall Ratings\n' +
                f'Total: {total:,} ratings | Labels: (count) [cumulative %]',
                fontsize=20, fontweight='bold', pad=20)
    
    # Add statistics
    stats_text = (
        f'Statistics:\n'
        f'─────────────\n'
        f'Mean:    {all_ratings.mean():.2f}\n'
        f'Median:  {np.median(all_ratings):.1f}\n'
        f'Std Dev: {all_ratings.std():.2f}\n'
        f'Mode:    {unique_vals[counts.argmax()]:.1f}'
    )
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
           fontsize=13, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85, edgecolor='black', linewidth=1.5),
           family='monospace', zorder=15)
    
    ax.tick_params(labelsize=14)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'all_overall_ratings_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def plot_avg_confidence_distribution(df, output_dir='outputs'):
    """
    Plot distribution of average confidence per submission
    """
    avg_confs = df[df['avg_confidence'].notna()]['avg_confidence']
    
    # Get counts for each unique value
    unique_vals, counts = np.unique(avg_confs.round(2), return_counts=True)
    total = len(avg_confs)
    cumsum = np.cumsum(counts)
    cumulative_pct = (cumsum / total) * 100
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create bars
    bars = ax.bar(range(len(unique_vals)), counts, 
                   color='mediumseagreen', edgecolor='black', linewidth=0.5, alpha=0.85)
    
    # Add labels (only for larger bars to avoid clutter)
    max_count = max(counts)
    for i, (val, count, cum_pct) in enumerate(zip(unique_vals, counts, cumulative_pct)):
        if count > max_count * 0.02:  # Only label if > 2% of max
            pct = (count / total) * 100
            ax.text(i, count + max_count * 0.01, 
                   f'{count:,}\n({pct:.1f}%)',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Labels
    ax.set_xticks(range(len(unique_vals)))
    ax.set_xticklabels([f'{v:.2f}' for v in unique_vals], 
                       fontsize=10, rotation=90, ha='center')
    ax.set_xlabel('Average Confidence per Submission', fontsize=18, fontweight='bold')
    ax.set_ylabel('Number of Submissions', fontsize=18, fontweight='bold')
    ax.set_title('Distribution of Average Confidence Ratings per Submission\n' +
                f'Total: {total:,} submissions',
                fontsize=20, fontweight='bold', pad=20)
    
    # Add statistics
    stats_text = (
        f'Statistics:\n'
        f'─────────────\n'
        f'Mean:    {avg_confs.mean():.3f}\n'
        f'Median:  {avg_confs.median():.3f}\n'
        f'Std Dev: {avg_confs.std():.3f}\n'
        f'Min:     {avg_confs.min():.2f}\n'
        f'Max:     {avg_confs.max():.2f}\n'
        f'─────────────\n'
        f'Q1 (25%): {avg_confs.quantile(0.25):.2f}\n'
        f'Q3 (75%): {avg_confs.quantile(0.75):.2f}'
    )
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
           fontsize=13, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85, edgecolor='black', linewidth=1.5),
           family='monospace', zorder=15)
    
    ax.tick_params(labelsize=14)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'avg_confidence_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def main(csv_file='data/ratings_data.csv', output_dir='outputs'):
    """
    Generate all distribution analyses
    """
    print("="*60)
    print("Distribution Analysis")
    print("="*60)
    
    # Load data
    df = pd.read_csv(csv_file)
    print(f"\nLoaded {len(df):,} submissions")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. Primary area distribution
    print("\n1. Generating primary area distribution...")
    area_counts = plot_primary_area_distribution(df, output_dir)
    
    print("\nTop 10 Primary Areas:")
    for area, count in area_counts.head(10).items():
        pct = (count / len(df)) * 100
        print(f"  {area[:60]:<60} {count:>5,} ({pct:>5.1f}%)")
    
    # Filter to submissions with reviews
    df_rated = df[df['num_reviews'] > 0].copy()
    print(f"\n{len(df_rated):,} submissions have reviews")
    
    # 2. All confidence ratings
    print("\n2. Generating all confidence ratings distribution...")
    plot_all_confidence_ratings(df_rated, output_dir)
    
    # 3. All overall ratings
    print("\n3. Generating all overall ratings distribution...")
    plot_all_overall_ratings(df_rated, output_dir)
    
    # 4. Average confidence distribution
    print("\n4. Generating average confidence distribution...")
    plot_avg_confidence_distribution(df_rated, output_dir)
    
    print("\n" + "="*60)
    print("✅ All plots generated successfully!")
    print(f"   Saved to: {output_dir}/")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'data/ratings_data.csv'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'outputs'
    
    main(csv_file, output_dir)

