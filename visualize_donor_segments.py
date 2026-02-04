#!/usr/bin/env python3
"""
Visualize donor segmentation with multiple graphs.
Creates comprehensive visualizations of donor segments and their donation patterns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_donor_segments():
    """Load donor segments data."""
    input_file = Path('donor_segments.csv')
    
    if not input_file.exists():
        print("✗ Error: donor_segments.csv not found. Run segment_election_donors.py first.")
        return None
    
    df = pd.read_csv(input_file)
    return df

def create_visualizations(df, diagrams_dir):
    """Create multiple visualizations of donor segments."""
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    
    # Color palette for segments
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Segment Distribution - Count
    ax1 = plt.subplot(2, 3, 1)
    segment_counts = df['Donor_Segment'].value_counts().reindex(segment_order)
    colors = [segment_colors[seg] for seg in segment_order]
    bars = ax1.bar(segment_order, segment_counts.values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax1.set_title('Number of Donors by Segment', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Number of Donors', fontsize=10)
    ax1.set_xlabel('Donor Segment', fontsize=10)
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 2. Segment Distribution - Percentage
    ax2 = plt.subplot(2, 3, 2)
    segment_pcts = (segment_counts / segment_counts.sum() * 100).reindex(segment_order)
    wedges, texts, autotexts = ax2.pie(segment_pcts.values, labels=segment_order, autopct='%1.1f%%',
                                        colors=colors, startangle=90, textprops={'fontsize': 10})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax2.set_title('Percentage of Donors by Segment', fontsize=12, fontweight='bold')
    
    # 3. Total Donated by Segment
    ax3 = plt.subplot(2, 3, 3)
    segment_totals = df.groupby('Donor_Segment')['Cumulative_Donation_USD'].sum().reindex(segment_order)
    bars = ax3.bar(segment_order, segment_totals.values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax3.set_title('Total Amount Donated by Segment', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Total Donation ($)', fontsize=10)
    ax3.set_xlabel('Donor Segment', fontsize=10)
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K'))
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'${height/1e6:.1f}M' if height >= 1e6 else f'${height/1e3:.0f}K',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 4. Donation Amount Distribution (Box Plot)
    ax4 = plt.subplot(2, 3, 4)
    df_sorted = df.copy()
    df_sorted['Donor_Segment'] = pd.Categorical(df_sorted['Donor_Segment'], categories=segment_order, ordered=True)
    bp = ax4.boxplot([df_sorted[df_sorted['Donor_Segment'] == seg]['Cumulative_Donation_USD'].values 
                       for seg in segment_order],
                      labels=segment_order, patch_artist=True)
    for patch, seg in zip(bp['boxes'], segment_order):
        patch.set_facecolor(segment_colors[seg])
        patch.set_alpha(0.7)
    ax4.set_title('Distribution of Donation Amounts by Segment', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Donation Amount ($)', fontsize=10)
    ax4.set_xlabel('Donor Segment', fontsize=10)
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K'))
    
    # 5. Average Donation by Segment
    ax5 = plt.subplot(2, 3, 5)
    avg_donations = df.groupby('Donor_Segment')['Cumulative_Donation_USD'].mean().reindex(segment_order)
    bars = ax5.bar(segment_order, avg_donations.values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax5.set_title('Average Donation per Donor by Segment', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Average Donation ($)', fontsize=10)
    ax5.set_xlabel('Donor Segment', fontsize=10)
    ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'${height/1e3:.1f}K',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 6. Number of Donations per Donor by Segment
    ax6 = plt.subplot(2, 3, 6)
    avg_num_donations = df.groupby('Donor_Segment')['Number_of_Donations'].mean().reindex(segment_order)
    bars = ax6.bar(segment_order, avg_num_donations.values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax6.set_title('Average Number of Donations per Donor', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Average Number of Donations', fontsize=10)
    ax6.set_xlabel('Donor Segment', fontsize=10)
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    
    # Save figure
    output_file = diagrams_dir / 'donor_segments_visualization.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved visualization to {output_file}")
    
    return fig

def create_cumulative_distribution(df, diagrams_dir):
    """Create cumulative distribution plot."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    # Sort by donation amount
    df_sorted = df.sort_values('Cumulative_Donation_USD')
    
    # Create cumulative distribution plot
    for segment in segment_order:
        segment_data = df_sorted[df_sorted['Donor_Segment'] == segment].sort_values('Cumulative_Donation_USD')
        cumulative_sum = segment_data['Cumulative_Donation_USD'].cumsum()
        cumulative_pct = cumulative_sum / cumulative_sum.iloc[-1] * 100
        
        ax.plot(range(len(segment_data)), cumulative_pct, 
               label=segment, color=segment_colors[segment], linewidth=2.5, marker='o', markersize=3, alpha=0.7)
    
    ax.set_title('Cumulative Donation Distribution by Segment', fontsize=14, fontweight='bold')
    ax.set_xlabel('Donor Rank (within segment)', fontsize=11)
    ax.set_ylabel('Cumulative % of Total Donations', fontsize=11)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 100])
    
    plt.tight_layout()
    
    # Save figure
    output_file = diagrams_dir / 'donor_cumulative_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved cumulative distribution to {output_file}")
    
    return fig

def create_statistics_table(df, diagrams_dir):
    """Create and save detailed statistics table."""
    
    # Calculate statistics by segment
    segment_order = ['Small', 'Medium', 'Large']
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    
    stats_data = []
    
    for segment in segment_order:
        segment_df = df[df['Donor_Segment'] == segment]
        
        stats_data.append({
            'Segment': segment,
            'Count': len(segment_df),
            'Percentage': f"{len(segment_df) / len(df) * 100:.2f}%",
            'Total Donated': f"${segment_df['Cumulative_Donation_USD'].sum():,.2f}",
            '% of Total': f"{segment_df['Cumulative_Donation_USD'].sum() / df['Cumulative_Donation_USD'].sum() * 100:.2f}%",
            'Average': f"${segment_df['Cumulative_Donation_USD'].mean():,.2f}",
            'Median': f"${segment_df['Cumulative_Donation_USD'].median():,.2f}",
            'Min': f"${segment_df['Cumulative_Donation_USD'].min():,.2f}",
            'Max': f"${segment_df['Cumulative_Donation_USD'].max():,.2f}",
            'Avg # Donations': f"{segment_df['Number_of_Donations'].mean():.2f}",
        })
    
    stats_df = pd.DataFrame(stats_data)
    
    # Save statistics table
    output_file = diagrams_dir / 'donor_segment_statistics.csv'
    stats_df.to_csv(output_file, index=False)
    print(f"  ✓ Saved statistics table to {output_file}")
    
    # Print to console
    print(f"\n{'='*80}")
    print("DONOR SEGMENT STATISTICS")
    print(f"{'='*80}\n")
    print(stats_df.to_string(index=False))
    print(f"\n{'='*80}\n")
    
    return stats_df

def main():
    """Main function."""
    print("="*80)
    print("VISUALIZE DONOR SEGMENTS")
    print("="*80)
    
    # Create diagrams folder
    diagrams_dir = Path('donor_segmentation_diagrams')
    diagrams_dir.mkdir(exist_ok=True)
    
    print(f"\n[1/5] Loading donor segments data...")
    df = load_donor_segments()
    
    if df is None:
        return
    
    print(f"  ✓ Loaded {len(df):,} donors")
    
    print(f"\n[2/5] Creating visualizations...")
    create_visualizations(df, diagrams_dir)
    
    print(f"\n[3/5] Creating cumulative distribution plot...")
    create_cumulative_distribution(df, diagrams_dir)
    
    print(f"\n[4/5] Generating statistics table...")
    create_statistics_table(df, diagrams_dir)
    
    print(f"\n[5/5] Creating summary documentation...")
    print(f"  ✓ Images saved to {diagrams_dir}/")
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Generated donor segment visualizations")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
