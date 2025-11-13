#!/usr/bin/env python3
"""
Generate simple visualizations for ICLR 2025 demo data (10 samples)
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


def plot_rating_distribution(csv_file='iclr_2025/iclr_2025_demo/ratings_data.csv',
                              output_dir='outputs/iclr_2025'):
    """
    Create rating distribution plot for demo data
    """
    # Load data
    df = pd.read_csv(csv_file)
    rated_df = df[df['avg_rating'].notna()].copy()
    
    print(f"Loaded {len(rated_df)} submissions with ratings")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Calculate statistics
    mean_rating = rated_df['avg_rating'].mean()
    median_rating = rated_df['avg_rating'].median()
    std_rating = rated_df['avg_rating'].std()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create histogram
    n, bins, patches = ax.hist(rated_df['avg_rating'], bins=8, 
                                edgecolor='black', linewidth=1.2, alpha=0.8)
    
    # Color gradient
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(patches)))
    for patch, color in zip(patches, colors):
        patch.set_facecolor(color)
    
    # Add mean and median lines
    ax.axvline(mean_rating, color='red', linestyle='--', linewidth=2.5,
               label=f'Mean: {mean_rating:.2f}', alpha=0.8)
    ax.axvline(median_rating, color='purple', linestyle='--', linewidth=2.5,
               label=f'Median: {median_rating:.2f}', alpha=0.8)
    
    # Labels
    ax.set_xlabel('Average Rating', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Submissions', fontsize=14, fontweight='bold')
    ax.set_title(f'ICLR 2025 Demo: Rating Distribution (n={len(rated_df)})\n'
                 f'Mean: {mean_rating:.2f} | Median: {median_rating:.2f} | Std: {std_rating:.2f}',
                 fontsize=16, fontweight='bold', pad=15)
    
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'demo_rating_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def plot_area_distribution(csv_file='iclr_2025/iclr_2025_demo/ratings_data.csv',
                           output_dir='outputs/iclr_2025'):
    """
    Plot primary area distribution
    """
    df = pd.read_csv(csv_file)
    area_counts = df['primary_area'].value_counts()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create horizontal bar chart
    bars = ax.barh(range(len(area_counts)), area_counts.values,
                    color='steelblue', edgecolor='black', linewidth=0.8, alpha=0.85)
    
    # Add count labels
    for i, count in enumerate(area_counts.values):
        ax.text(count + 0.1, i, f'{count}',
               ha='left', va='center', fontsize=11, fontweight='bold')
    
    # Labels
    ax.set_yticks(range(len(area_counts)))
    ax.set_yticklabels(area_counts.index, fontsize=10)
    ax.set_xlabel('Number of Submissions', fontsize=13, fontweight='bold')
    ax.set_ylabel('Primary Research Area', fontsize=13, fontweight='bold')
    ax.set_title('ICLR 2025 Demo: Submissions by Research Area (n=10)',
                fontsize=15, fontweight='bold', pad=15)
    
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'demo_area_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def plot_confidence_distribution(csv_file='iclr_2025/iclr_2025_demo/ratings_data.csv',
                                 output_dir='outputs/iclr_2025'):
    """
    Plot reviewer confidence distribution
    """
    df = pd.read_csv(csv_file)
    
    # Parse all confidence ratings
    all_confidences = []
    for conf_str in df['confidences']:
        try:
            confs = ast.literal_eval(conf_str)
            for c in confs:
                if isinstance(c, (int, float)):
                    all_confidences.append(c)
                elif isinstance(c, str):
                    try:
                        all_confidences.append(int(c.split(':')[0]))
                    except:
                        pass
        except:
            pass
    
    if not all_confidences:
        print("⚠ No confidence data to plot")
        return
    
    all_confidences = np.array(all_confidences)
    unique_vals, counts = np.unique(all_confidences, return_counts=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = ax.bar(unique_vals, counts, color='coral', 
                   edgecolor='black', linewidth=1, alpha=0.85, width=0.6)
    
    # Add count labels
    for val, count in zip(unique_vals, counts):
        ax.text(val, count + 0.2, f'{count}',
               ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Labels
    ax.set_xlabel('Confidence Level', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Reviews', fontsize=14, fontweight='bold')
    ax.set_title(f'ICLR 2025 Demo: Reviewer Confidence Distribution\n'
                 f'Total Reviews: {len(all_confidences)} | '
                 f'Mean Confidence: {all_confidences.mean():.2f}',
                 fontsize=16, fontweight='bold', pad=15)
    
    ax.set_xticks(unique_vals)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'demo_confidence_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def plot_reviews_per_paper(csv_file='iclr_2025/iclr_2025_demo/ratings_data.csv',
                           output_dir='outputs/iclr_2025'):
    """
    Plot distribution of reviews per paper
    """
    df = pd.read_csv(csv_file)
    review_counts = df['num_reviews'].value_counts().sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(review_counts.index, review_counts.values,
                   color='mediumseagreen', edgecolor='black', 
                   linewidth=1, alpha=0.85, width=0.6)
    
    # Add labels
    for num_reviews, count in zip(review_counts.index, review_counts.values):
        ax.text(num_reviews, count + 0.15, f'{count}',
               ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Number of Reviews', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Submissions', fontsize=14, fontweight='bold')
    ax.set_title(f'ICLR 2025 Demo: Reviews per Submission\n'
                 f'Average: {df["num_reviews"].mean():.2f} reviews/paper',
                 fontsize=16, fontweight='bold', pad=15)
    
    ax.set_xticks(review_counts.index)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'demo_reviews_per_paper.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def plot_decision_distribution(csv_file='iclr_2025/iclr_2025_demo/ratings_data.csv',
                                output_dir='outputs/iclr_2025'):
    """
    Plot decision distribution (Accept/Reject/Withdrawn breakdown)
    """
    df = pd.read_csv(csv_file)
    decision_counts = df['decision'].value_counts()
    
    # Define colors for each decision type
    colors_map = {
        'Accept (Oral)': '#1a9850',
        'Accept (Spotlight)': '#66bd63',
        'Accept (Poster)': '#a6d96a',
        'Reject': '#d73027',
        'Desk Reject': '#f46d43',
        'Withdrawn': '#fee090'
    }
    colors = [colors_map.get(d, 'gray') for d in decision_counts.index]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(range(len(decision_counts)), decision_counts.values,
                   color=colors, edgecolor='black', linewidth=1.2, alpha=0.9)
    
    # Add labels
    total = len(df)
    for i, (decision, count) in enumerate(zip(decision_counts.index, decision_counts.values)):
        pct = (count / total) * 100
        ax.text(i, count + 0.15, f'{count}\n({pct:.1f}%)',
               ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_xticks(range(len(decision_counts)))
    ax.set_xticklabels(decision_counts.index, fontsize=12, rotation=15, ha='right')
    ax.set_ylabel('Number of Submissions', fontsize=14, fontweight='bold')
    ax.set_title(f'ICLR 2025 Demo: Decision Distribution (n={total})',
                fontsize=16, fontweight='bold', pad=15)
    
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'demo_decision_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def plot_rating_by_decision(csv_file='iclr_2025/iclr_2025_demo/ratings_data.csv',
                            output_dir='outputs/iclr_2025'):
    """
    Plot rating distributions grouped by decision type
    """
    df = pd.read_csv(csv_file)
    df_rated = df[df['avg_rating'].notna()].copy()
    
    # Group by decision type
    decision_types = ['Accept', 'Reject', 'Withdrawn']
    data_by_decision = []
    labels = []
    colors_list = ['#66bd63', '#d73027', '#fee090']
    
    for decision_type in decision_types:
        ratings = df_rated[df_rated['decision_type'] == decision_type]['avg_rating'].values
        if len(ratings) > 0:
            data_by_decision.append(ratings)
            labels.append(f'{decision_type}\n(n={len(ratings)})')
    
    if not data_by_decision:
        print("⚠ No rating data to plot by decision")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create box plot
    bp = ax.boxplot(data_by_decision, labels=labels, patch_artist=True,
                     widths=0.6, showmeans=True,
                     meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
    
    # Color the boxes
    for patch, color in zip(bp['boxes'], colors_list[:len(data_by_decision)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # Add mean values as text
    for i, ratings in enumerate(data_by_decision):
        mean_val = ratings.mean()
        median_val = np.median(ratings)
        ax.text(i+1, ax.get_ylim()[1] * 0.95, 
               f'Mean: {mean_val:.2f}\nMedian: {median_val:.2f}',
               ha='center', va='top', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_ylabel('Average Rating', fontsize=14, fontweight='bold')
    ax.set_title('ICLR 2025 Demo: Rating Distribution by Decision Type',
                fontsize=16, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.tight_layout()
    
    output_file = Path(output_dir) / 'demo_rating_by_decision.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: {output_file}")
    plt.close()


def main():
    """
    Generate all demo visualizations
    """
    print("="*60)
    print("ICLR 2025 Demo Visualization Generator")
    print("="*60)
    print()
    
    csv_file = 'iclr_2025/iclr_2025_demo/ratings_data.csv'
    output_dir = 'outputs/iclr_2025'
    
    print("Generating plots...")
    print()
    
    # Generate all plots
    plot_rating_distribution(csv_file, output_dir)
    plot_area_distribution(csv_file, output_dir)
    plot_confidence_distribution(csv_file, output_dir)
    plot_reviews_per_paper(csv_file, output_dir)
    plot_decision_distribution(csv_file, output_dir)
    plot_rating_by_decision(csv_file, output_dir)
    
    print()
    print("="*60)
    print("✅ All demo visualizations complete!")
    print(f"📁 Saved to: {output_dir}/")
    print(f"📊 Generated 6 plots including decision analysis")
    print("="*60)


if __name__ == "__main__":
    main()
