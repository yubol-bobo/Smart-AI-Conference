#!/usr/bin/env python3
"""
Generate decision-related visualizations for conference submissions.
Only generates plots if decision information is available in the data.

Usage:
    python3 src/plot_decisions.py <ratings_csv> <output_dir>
    
Example:
    python3 src/plot_decisions.py iclr_2025/iclr_2025_v1/ratings_data.csv outputs/iclr_2025/
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def check_decisions_available(df):
    """Check if decision information is available in the dataframe"""
    if 'decision' not in df.columns or 'decision_type' not in df.columns:
        return False
    
    # Check if we have actual decisions (not all "Pending")
    if df['decision'].notna().sum() == 0:
        return False
    
    # Check if we have non-pending decisions
    non_pending = df[df['decision'] != 'Pending']
    return len(non_pending) > 0


def plot_decision_distribution(df, output_dir):
    """Plot overall decision distribution - one bar per decision type with counts"""
    # Filter out pending decisions
    df_decided = df[df['decision'] != 'Pending'].copy()
    
    if len(df_decided) == 0:
        print("  ⚠ No decided submissions found, skipping decision distribution")
        return
    
    # Get decision type counts and sort by count
    decision_type_counts = df_decided['decision_type'].value_counts().sort_values(ascending=False)
    
    # Define colors for each decision type
    colors_type = {
        'Oral': '#e74c3c',           # Red
        'Spotlight': '#f39c12',       # Orange
        'Poster': '#2ecc71',          # Green
        'Reject': '#95a5a6',          # Gray
        'Desk Reject': '#7f8c8d',     # Dark Gray
        'Withdrawn': '#bdc3c7'        # Light Gray
    }
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create bars
    bars = ax.bar(range(len(decision_type_counts)), 
                  decision_type_counts.values,
                  color=[colors_type.get(d, '#34495e') for d in decision_type_counts.index],
                  edgecolor='black',
                  linewidth=1.5)
    
    # Set labels
    ax.set_xticks(range(len(decision_type_counts)))
    ax.set_xticklabels(decision_type_counts.index, fontsize=13, fontweight='bold')
    ax.set_ylabel('Number of Submissions', fontsize=14, fontweight='bold')
    ax.set_title('Decision Distribution', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add counts and percentages on bars
    total = decision_type_counts.sum()
    for i, (bar, count) in enumerate(zip(bars, decision_type_counts.values)):
        height = bar.get_height()
        percentage = (count / total) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{count:,}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Add total count text
    ax.text(0.98, 0.98, f'Total: {total:,} submissions',
            transform=ax.transAxes, fontsize=12, fontweight='bold',
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black', linewidth=1.5))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'decision_distribution.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: {output_path}")


def plot_rating_by_decision(df, output_dir):
    """Plot rating distributions by decision type"""
    # Filter out pending and submissions without ratings
    df_decided = df[(df['decision'] != 'Pending') & (df['avg_rating'].notna())].copy()
    
    if len(df_decided) == 0:
        print("  ⚠ No decided submissions with ratings found, skipping rating by decision")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Order decision types
    decision_order = ['Oral', 'Spotlight', 'Poster', 'Reject', 'Desk Reject', 'Withdrawn']
    decision_types_present = [d for d in decision_order if d in df_decided['decision_type'].values]
    
    # Create violin plot
    parts = ax.violinplot(
        [df_decided[df_decided['decision_type'] == dt]['avg_rating'].values 
         for dt in decision_types_present],
        positions=range(len(decision_types_present)),
        widths=0.7,
        showmeans=True,
        showextrema=True
    )
    
    # Color the violin plots
    colors = {
        'Oral': '#e74c3c',
        'Spotlight': '#f39c12',
        'Poster': '#3498db',
        'Reject': '#95a5a6',
        'Desk Reject': '#7f8c8d',
        'Withdrawn': '#bdc3c7'
    }
    
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors.get(decision_types_present[i], '#34495e'))
        pc.set_alpha(0.7)
    
    # Add box plots on top
    box_parts = ax.boxplot(
        [df_decided[df_decided['decision_type'] == dt]['avg_rating'].values 
         for dt in decision_types_present],
        positions=range(len(decision_types_present)),
        widths=0.3,
        patch_artist=True,
        showfliers=False
    )
    
    for i, patch in enumerate(box_parts['boxes']):
        patch.set_facecolor('white')
        patch.set_alpha(0.5)
    
    ax.set_xticks(range(len(decision_types_present)))
    ax.set_xticklabels(decision_types_present, fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Rating', fontsize=12, fontweight='bold')
    ax.set_xlabel('Decision Type', fontsize=12, fontweight='bold')
    ax.set_title('Rating Distribution by Decision Type', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    # Add mean values
    for i, dt in enumerate(decision_types_present):
        mean_rating = df_decided[df_decided['decision_type'] == dt]['avg_rating'].mean()
        count = len(df_decided[df_decided['decision_type'] == dt])
        ax.text(i, ax.get_ylim()[1] * 0.95, f'μ={mean_rating:.2f}\nn={count:,}',
                ha='center', va='top', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'rating_by_decision.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: {output_path}")


def plot_acceptance_rate_by_area(df, output_dir, min_submissions=50):
    """Plot acceptance rates by research area"""
    # Filter decided submissions
    df_decided = df[df['decision'] != 'Pending'].copy()
    
    if len(df_decided) == 0:
        print("  ⚠ No decided submissions found, skipping acceptance by area")
        return
    
    # Calculate acceptance rates by area
    area_stats = []
    for area in df_decided['primary_area'].unique():
        area_df = df_decided[df_decided['primary_area'] == area]
        total = len(area_df)
        
        if total >= min_submissions:
            accepted = len(area_df[area_df['decision'] == 'Accept'])
            acceptance_rate = (accepted / total) * 100
            area_stats.append({
                'area': area,
                'total': total,
                'accepted': accepted,
                'acceptance_rate': acceptance_rate
            })
    
    if not area_stats:
        print(f"  ⚠ No areas with ≥{min_submissions} submissions, skipping acceptance by area")
        return
    
    # Convert to dataframe and sort
    area_df = pd.DataFrame(area_stats).sort_values('acceptance_rate', ascending=True)
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, max(8, len(area_df) * 0.4)))
    
    # Create color gradient
    colors = plt.cm.RdYlGn(area_df['acceptance_rate'].values / area_df['acceptance_rate'].max())
    
    bars = ax.barh(range(len(area_df)), area_df['acceptance_rate'].values, color=colors)
    ax.set_yticks(range(len(area_df)))
    
    # Truncate long area names
    labels = [area[:60] + '...' if len(area) > 60 else area for area in area_df['area'].values]
    ax.set_yticklabels(labels, fontsize=10)
    
    ax.set_xlabel('Acceptance Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Acceptance Rate by Research Area', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    
    # Add percentage labels
    for i, (bar, row) in enumerate(zip(bars, area_df.itertuples())):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                f'{row.acceptance_rate:.1f}% ({row.accepted}/{row.total})',
                ha='left', va='center', fontsize=9, fontweight='bold')
    
    # Add overall acceptance rate line
    overall_acceptance = (df_decided['decision'] == 'Accept').sum() / len(df_decided) * 100
    ax.axvline(overall_acceptance, color='red', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Overall: {overall_acceptance:.1f}%')
    ax.legend(fontsize=11, loc='lower right')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'acceptance_rate_by_area.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: {output_path}")


def plot_rating_threshold_analysis(df, output_dir):
    """Analyze rating thresholds for different decision types"""
    df_decided = df[(df['decision'] != 'Pending') & (df['avg_rating'].notna())].copy()
    
    if len(df_decided) == 0:
        print("  ⚠ No decided submissions with ratings, skipping threshold analysis")
        return
    
    # Get accept/reject data
    accepted = df_decided[df_decided['decision'] == 'Accept']['avg_rating'].values
    rejected = df_decided[df_decided['decision'] == 'Reject']['avg_rating'].values
    
    if len(accepted) == 0 or len(rejected) == 0:
        print("  ⚠ Missing accept or reject data, skipping threshold analysis")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create overlapping histograms
    bins = np.arange(1, 10.5, 0.25)
    ax.hist(rejected, bins=bins, alpha=0.6, label='Rejected', color='#e74c3c', edgecolor='black')
    ax.hist(accepted, bins=bins, alpha=0.6, label='Accepted', color='#2ecc71', edgecolor='black')
    
    # Add vertical lines for means
    ax.axvline(rejected.mean(), color='#c0392b', linestyle='--', linewidth=2,
               label=f'Reject Mean: {rejected.mean():.2f}')
    ax.axvline(accepted.mean(), color='#27ae60', linestyle='--', linewidth=2,
               label=f'Accept Mean: {accepted.mean():.2f}')
    
    ax.set_xlabel('Average Rating', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Submissions', fontsize=12, fontweight='bold')
    ax.set_title('Rating Distribution: Accepted vs Rejected', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    
    # Add statistics text
    stats_text = f"""Accept: n={len(accepted):,}, μ={accepted.mean():.2f}, σ={accepted.std():.2f}
Reject: n={len(rejected):,}, μ={rejected.mean():.2f}, σ={rejected.std():.2f}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'rating_threshold_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: {output_path}")


def main(ratings_file, output_dir):
    """Generate all decision-related visualizations"""
    print("="*60)
    print("Decision Analysis Visualizations")
    print("="*60)
    
    # Load data
    print(f"\nLoading data from {ratings_file}...")
    df = pd.read_csv(ratings_file)
    print(f"✓ Loaded {len(df):,} submissions")
    
    # Check if decisions are available
    if not check_decisions_available(df):
        print("\n⚠ No decision information available in this dataset.")
        print("  Decision visualizations will be skipped.")
        print("  (This is normal for current/ongoing conferences)")
        return
    
    print("\n✓ Decision information detected!")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Count decided submissions
    decided_count = len(df[df['decision'] != 'Pending'])
    print(f"  Decided submissions: {decided_count:,} / {len(df):,}")
    
    print("\nGenerating decision visualizations...")
    
    # Generate plots
    print("\n1. Decision distribution...")
    plot_decision_distribution(df, output_dir)
    
    print("\n2. Rating by decision type...")
    plot_rating_by_decision(df, output_dir)
    
    print("\n3. Acceptance rate by area...")
    plot_acceptance_rate_by_area(df, output_dir)
    
    print("\n4. Rating threshold analysis...")
    plot_rating_threshold_analysis(df, output_dir)
    
    print("\n" + "="*60)
    print("✅ Decision visualizations complete!")
    print(f"   Saved to: {output_dir}")
    print("="*60)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 src/plot_decisions.py <ratings_csv> <output_dir>")
        print("\nExample:")
        print("  python3 src/plot_decisions.py iclr_2025/iclr_2025_v1/ratings_data.csv outputs/iclr_2025/")
        sys.exit(1)
    
    ratings_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(ratings_file):
        print(f"❌ Error: File not found: {ratings_file}")
        sys.exit(1)
    
    main(ratings_file, output_dir)
