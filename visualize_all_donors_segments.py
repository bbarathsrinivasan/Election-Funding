#!/usr/bin/env python3
"""
Generate comprehensive donor segmentation visualizations for all US Election donors.
Creates individual graphs with detailed analysis and interpretation guides.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_and_segment_donors():
    """Load donor data and segment by percentiles."""
    
    # Input file - use full dataset
    input_file = Path('US_Election_Donation.csv')
    
    if not input_file.exists():
        print("✗ Error: US_Election_Donation.csv not found.")
        return None
    
    print(f"\n[1/2] Loading full donation data (this may take a moment)...")
    
    # Load donation data in chunks to handle large files
    try:
        chunks = []
        chunk_size = 50000
        for chunk in pd.read_csv(input_file, chunksize=chunk_size, low_memory=False):
            chunks.append(chunk)
        
        df = pd.concat(chunks, ignore_index=True)
        print(f"  ✓ Loaded {len(df):,} total donation records")
    except Exception as e:
        print(f"  ✗ Error loading file: {e}")
        return None
    
    # Check required columns
    required_columns = ['Donator', 'Donation_Amount_USD']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"  ✗ Missing required columns: {', '.join(missing_columns)}")
        return None
    
    print(f"\n[2/2] Calculating percentile thresholds and segmenting donors...")
    
    # Handle missing or zero values
    df['Donation_Amount_USD'] = pd.to_numeric(df['Donation_Amount_USD'], errors='coerce').fillna(0)
    
    # Aggregate by donor
    donor_stats = df.groupby('Donator').agg({
        'Donation_Amount_USD': ['sum', 'count'],
    }).reset_index()
    
    # Flatten column names
    donor_stats.columns = ['Donator', 'Cumulative_Donation_USD', 'Number_of_Donations']
    
    # Remove donors with zero cumulative donations
    donor_stats = donor_stats[donor_stats['Cumulative_Donation_USD'] > 0]
    
    # Calculate percentile thresholds
    p33_3 = donor_stats['Cumulative_Donation_USD'].quantile(0.333)
    p66_6 = donor_stats['Cumulative_Donation_USD'].quantile(0.666)
    
    print(f"  ✓ 33.3rd percentile: ${p33_3:,.2f}")
    print(f"  ✓ 66.6th percentile: ${p66_6:,.2f}")
    
    # Classify donors into segments
    def classify_segment(cumulative_donation):
        if cumulative_donation <= p33_3:
            return 'Small'
        elif cumulative_donation <= p66_6:
            return 'Medium'
        else:
            return 'Large'
    
    donor_stats['Donor_Segment'] = donor_stats['Cumulative_Donation_USD'].apply(classify_segment)
    
    print(f"  ✓ Segmented {len(donor_stats):,} unique donors")
    
    return donor_stats

def ensure_output_dir():
    """Ensure output directory exists."""
    output_dir = Path('donor_segmentation_diagrams')
    output_dir.mkdir(exist_ok=True)
    return output_dir

def create_segment_count_chart(df, output_dir):
    """Create bar chart of donor counts by segment."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    segment_counts = df['Donor_Segment'].value_counts().reindex(segment_order)
    colors = [segment_colors[seg] for seg in segment_order]
    
    bars = ax.bar(segment_order, segment_counts.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    ax.set_title('Number of Donors by Segment', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Number of Donors', fontsize=12)
    ax.set_xlabel('Donor Segment', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_dir / '01_segment_count.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 01_segment_count.png")
    return output_file

def create_segment_percentage_chart(df, output_dir):
    """Create pie chart of donor percentages by segment."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    segment_counts = df['Donor_Segment'].value_counts().reindex(segment_order)
    colors = [segment_colors[seg] for seg in segment_order]
    
    wedges, texts, autotexts = ax.pie(segment_counts.values, 
                                       labels=segment_order, 
                                       autopct='%1.1f%%',
                                       colors=colors, 
                                       startangle=90,
                                       textprops={'fontsize': 11},
                                       wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    ax.set_title('Percentage Distribution of Donors by Segment', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_file = output_dir / '02_segment_percentage.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 02_segment_percentage.png")
    return output_file

def create_total_donations_chart(df, output_dir):
    """Create bar chart of total donations by segment."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    segment_totals = df.groupby('Donor_Segment')['Cumulative_Donation_USD'].sum().reindex(segment_order)
    colors = [segment_colors[seg] for seg in segment_order]
    
    bars = ax.bar(segment_order, segment_totals.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    ax.set_title('Total Amount Donated by Segment', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Total Donation ($)', fontsize=12)
    ax.set_xlabel('Donor Segment', fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M' if x >= 1e6 else f'${x/1e3:.0f}K'))
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        label = f'${height/1e6:.1f}M' if height >= 1e6 else f'${height/1e3:.0f}K'
        ax.text(bar.get_x() + bar.get_width()/2., height,
                label,
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_dir / '03_total_donations.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 03_total_donations.png")
    return output_file

def create_total_donations_percentage_chart(df, output_dir):
    """Create pie chart of donation percentage by segment."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    segment_totals = df.groupby('Donor_Segment')['Cumulative_Donation_USD'].sum().reindex(segment_order)
    colors = [segment_colors[seg] for seg in segment_order]
    
    wedges, texts, autotexts = ax.pie(segment_totals.values, 
                                       labels=segment_order, 
                                       autopct='%1.1f%%',
                                       colors=colors, 
                                       startangle=90,
                                       textprops={'fontsize': 11},
                                       wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    ax.set_title('Percentage of Total Donations by Segment', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_file = output_dir / '04_total_donations_percentage.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 04_total_donations_percentage.png")
    return output_file

def create_average_donation_chart(df, output_dir):
    """Create bar chart of average donations by segment."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    avg_donations = df.groupby('Donor_Segment')['Cumulative_Donation_USD'].mean().reindex(segment_order)
    colors = [segment_colors[seg] for seg in segment_order]
    
    bars = ax.bar(segment_order, avg_donations.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    ax.set_title('Average Donation Amount per Donor by Segment', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Average Donation ($)', fontsize=12)
    ax.set_xlabel('Donor Segment', fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K' if x >= 1e3 else f'${x:.0f}'))
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        label = f'${height/1e3:.1f}K' if height >= 1e3 else f'${height:.0f}'
        ax.text(bar.get_x() + bar.get_width()/2., height,
                label,
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_dir / '05_average_donation.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 05_average_donation.png")
    return output_file

def create_median_donation_chart(df, output_dir):
    """Create bar chart of median donations by segment."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    median_donations = df.groupby('Donor_Segment')['Cumulative_Donation_USD'].median().reindex(segment_order)
    colors = [segment_colors[seg] for seg in segment_order]
    
    bars = ax.bar(segment_order, median_donations.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    ax.set_title('Median Donation Amount per Donor by Segment', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Median Donation ($)', fontsize=12)
    ax.set_xlabel('Donor Segment', fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K' if x >= 1e3 else f'${x:.0f}'))
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        label = f'${height/1e3:.1f}K' if height >= 1e3 else f'${height:.0f}'
        ax.text(bar.get_x() + bar.get_width()/2., height,
                label,
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_dir / '06_median_donation.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 06_median_donation.png")
    return output_file

def create_donation_distribution_boxplot(df, output_dir):
    """Create box plot of donation distributions by segment."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    df_sorted = df.copy()
    df_sorted['Donor_Segment'] = pd.Categorical(df_sorted['Donor_Segment'], 
                                                 categories=segment_order, ordered=True)
    
    bp = ax.boxplot([df_sorted[df_sorted['Donor_Segment'] == seg]['Cumulative_Donation_USD'].values 
                      for seg in segment_order],
                     tick_labels=segment_order,
                     patch_artist=True,
                     widths=0.6)
    
    for patch, seg in zip(bp['boxes'], segment_order):
        patch.set_facecolor(segment_colors[seg])
        patch.set_alpha(0.7)
    
    ax.set_title('Distribution of Donation Amounts by Segment (Box Plot)', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Donation Amount ($)', fontsize=12)
    ax.set_xlabel('Donor Segment', fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K' if x >= 1e3 else f'${x:.0f}'))
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = output_dir / '07_donation_distribution_boxplot.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 07_donation_distribution_boxplot.png")
    return output_file

def create_average_frequency_chart(df, output_dir):
    """Create bar chart of average donation frequency by segment."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    avg_frequency = df.groupby('Donor_Segment')['Number_of_Donations'].mean().reindex(segment_order)
    colors = [segment_colors[seg] for seg in segment_order]
    
    bars = ax.bar(segment_order, avg_frequency.values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    ax.set_title('Average Number of Donations per Donor by Segment', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Average Number of Donations', fontsize=12)
    ax.set_xlabel('Donor Segment', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_dir / '08_average_frequency.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 08_average_frequency.png")
    return output_file

def create_cumulative_distribution_chart(df, output_dir):
    """Create cumulative distribution plot."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    segment_colors = {'Small': '#3498db', 'Medium': '#f39c12', 'Large': '#e74c3c'}
    segment_order = ['Small', 'Medium', 'Large']
    
    # Sort by donation amount
    df_sorted = df.sort_values('Cumulative_Donation_USD')
    
    # Create cumulative distribution plot
    for segment in segment_order:
        segment_data = df_sorted[df_sorted['Donor_Segment'] == segment].sort_values('Cumulative_Donation_USD')
        cumulative_sum = segment_data['Cumulative_Donation_USD'].cumsum()
        cumulative_pct = cumulative_sum / cumulative_sum.iloc[-1] * 100 if len(cumulative_sum) > 0 else []
        
        ax.plot(range(len(segment_data)), cumulative_pct, 
               label=segment, color=segment_colors[segment], linewidth=2.5, marker='o', markersize=3, alpha=0.7)
    
    ax.set_title('Cumulative Distribution of Donations by Segment', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Donor Rank (within segment)', fontsize=12)
    ax.set_ylabel('Cumulative % of Total Donations', fontsize=12)
    ax.legend(fontsize=11, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 105])
    
    plt.tight_layout()
    output_file = output_dir / '09_cumulative_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created: 09_cumulative_distribution.png")
    return output_file

def create_statistics_csv(df, output_dir):
    """Create detailed statistics CSV."""
    segment_order = ['Small', 'Medium', 'Large']
    
    stats_data = []
    
    for segment in segment_order:
        segment_df = df[df['Donor_Segment'] == segment]
        
        stats_data.append({
            'Segment': segment,
            'Count': len(segment_df),
            'Percentage': f"{len(segment_df) / len(df) * 100:.2f}%",
            'Total_Donated': f"${segment_df['Cumulative_Donation_USD'].sum():,.2f}",
            'Pct_of_Total': f"{segment_df['Cumulative_Donation_USD'].sum() / df['Cumulative_Donation_USD'].sum() * 100:.2f}%",
            'Average': f"${segment_df['Cumulative_Donation_USD'].mean():,.2f}",
            'Median': f"${segment_df['Cumulative_Donation_USD'].median():,.2f}",
            'Min': f"${segment_df['Cumulative_Donation_USD'].min():,.2f}",
            'Max': f"${segment_df['Cumulative_Donation_USD'].max():,.2f}",
            'Std_Dev': f"${segment_df['Cumulative_Donation_USD'].std():,.2f}",
            'Avg_Num_Donations': f"{segment_df['Number_of_Donations'].mean():.2f}",
        })
    
    stats_df = pd.DataFrame(stats_data)
    output_file = output_dir / 'all_donors_segment_statistics.csv'
    stats_df.to_csv(output_file, index=False)
    print(f"  ✓ Created: all_donors_segment_statistics.csv")
    
    return stats_df

def print_summary(df):
    """Print summary statistics."""
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS - ALL US ELECTION DONORS")
    print(f"{'='*80}\n")
    
    print(f"Total Donors: {len(df):,}")
    print(f"Total Donations: ${df['Cumulative_Donation_USD'].sum():,.2f}")
    print(f"Average per Donor: ${df['Cumulative_Donation_USD'].mean():,.2f}")
    print(f"Median per Donor: ${df['Cumulative_Donation_USD'].median():,.2f}")
    
    print(f"\nSegment Distribution:")
    segment_order = ['Small', 'Medium', 'Large']
    for segment in segment_order:
        segment_df = df[df['Donor_Segment'] == segment]
        count = len(segment_df)
        pct = (count / len(df) * 100)
        total = segment_df['Cumulative_Donation_USD'].sum()
        total_pct = (total / df['Cumulative_Donation_USD'].sum() * 100)
        
        print(f"\n  {segment} Donors:")
        print(f"    Count: {count:,} ({pct:.2f}%)")
        print(f"    Total: ${total:,.2f} ({total_pct:.2f}%)")
        print(f"    Avg: ${segment_df['Cumulative_Donation_USD'].mean():,.2f}")

def main():
    """Main function."""
    print("="*80)
    print("GENERATE ALL DONOR SEGMENTATION VISUALIZATIONS")
    print("="*80)
    
    # Load and segment data
    df = load_and_segment_donors()
    if df is None:
        return
    
    # Create output directory
    output_dir = ensure_output_dir()
    
    print(f"\nGenerating individual visualizations...")
    
    # Create all visualizations
    create_segment_count_chart(df, output_dir)
    create_segment_percentage_chart(df, output_dir)
    create_total_donations_chart(df, output_dir)
    create_total_donations_percentage_chart(df, output_dir)
    create_average_donation_chart(df, output_dir)
    create_median_donation_chart(df, output_dir)
    create_donation_distribution_boxplot(df, output_dir)
    create_average_frequency_chart(df, output_dir)
    create_cumulative_distribution_chart(df, output_dir)
    
    print(f"\nGenerating statistics table...")
    create_statistics_csv(df, output_dir)
    
    # Print summary
    print_summary(df)
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Generated all visualizations")
    print(f"  Output directory: {output_dir}/")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
