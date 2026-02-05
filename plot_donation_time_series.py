#!/usr/bin/env python3
"""
Generate donation time series visualizations.
Creates 32 plots:
- 8 cumulative ratio plots for Dem: (Dem + Rep) / Dem
- 8 cumulative ratio plots for Rep: (Dem + Rep) / Rep
- 8 Democratic donation time series plots
- 8 Republican donation time series plots
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10

def load_aggregations():
    """Load weekly and monthly aggregation data."""
    data_dir = Path('donation_time_series_data')
    
    weekly_file = data_dir / 'weekly_aggregations.csv'
    monthly_file = data_dir / 'monthly_aggregations.csv'
    
    if not weekly_file.exists() or not monthly_file.exists():
        print("✗ Error: Aggregation files not found")
        print("  Run prepare_donation_time_series.py first")
        return None, None
    
    weekly_df = pd.read_csv(weekly_file)
    monthly_df = pd.read_csv(monthly_file)
    
    return weekly_df, monthly_df

def prepare_ratio_data(df, time_col, segment=None):
    """
    Prepare data for ratio plots.
    Calculate (Dem + Rep) / Dem and (Dem + Rep) / Rep
    """
    # Filter by segment if specified
    if segment:
        df = df[df['Donor_Segment'] == segment].copy()
    
    # Pivot to get DEM and REP columns
    pivot = df.pivot_table(
        index=time_col, 
        columns='Party', 
        values='Total_Donation', 
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Ensure both DEM and REP columns exist
    if 'DEM' not in pivot.columns:
        pivot['DEM'] = 0
    if 'REP' not in pivot.columns:
        pivot['REP'] = 0
    
    # Calculate ratios
    pivot['Total'] = pivot['DEM'] + pivot['REP']
    
    # Avoid division by zero
    pivot['Dem_Ratio'] = pivot.apply(
        lambda row: (row['Total'] / row['DEM']) if row['DEM'] > 0 else np.nan,
        axis=1
    )
    pivot['Rep_Ratio'] = pivot.apply(
        lambda row: (row['Total'] / row['REP']) if row['REP'] > 0 else np.nan,
        axis=1
    )
    
    return pivot

def prepare_party_data(df, time_col, party, segment=None):
    """Prepare time series data for a specific party."""
    # Filter by party
    df = df[df['Party'] == party].copy()
    
    # Filter by segment if specified
    if segment:
        df = df[df['Donor_Segment'] == segment].copy()
    
    # Group by time
    result = df.groupby(time_col)['Total_Donation'].sum().reset_index()
    result.columns = [time_col, 'Total_Donation']
    
    return result

def plot_ratio(data, time_col, ratio_col, party_name, frequency, segment_name, output_dir, log_scale=False):
    """Plot cumulative ratio over time."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Remove NaN values for plotting
    plot_data = data[[time_col, ratio_col]].dropna()
    
    if len(plot_data) == 0:
        print(f"  Warning: No valid data for {party_name} ratio ({frequency}, {segment_name})")
        plt.close()
        return
    
    # Plot
    ax.plot(range(len(plot_data)), plot_data[ratio_col], 
            linewidth=2, color='#2E86AB' if party_name == 'Democratic' else '#A23B72',
            marker='o', markersize=3, alpha=0.7)
    
    # Add horizontal reference line at 2.0 (equal donations)
    ax.axhline(y=2.0, color='gray', linestyle='--', alpha=0.5, label='Equal Donations (2.0)')
    
    # Formatting
    ax.set_xlabel(f'{frequency.capitalize()} Period', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'Cumulative Ratio\n(Dem + Rep) / {party_name[:3]}', fontsize=12, fontweight='bold')
    
    title = f'{party_name} Donation Ratio - {frequency.capitalize()}'
    if segment_name != 'All':
        title += f' ({segment_name} Donors)'
    if log_scale:
        title += ' [Log Scale]'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Set x-axis labels (show every nth label to avoid crowding)
    step = max(1, len(plot_data) // 15)
    x_positions = range(0, len(plot_data), step)
    x_labels = plot_data[time_col].iloc[::step].tolist()
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    
    if log_scale:
        ax.set_yscale('log')

    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save
    party_short = 'dem' if party_name == 'Democratic' else 'rep'
    segment_short = segment_name.lower()
    log_suffix = '_log' if log_scale else ''
    filename = f'cumulative_ratio_{frequency}_{segment_short}_{party_short}{log_suffix}.png'
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: {filename}")

def plot_party_donations(data, time_col, party_name, frequency, segment_name, output_dir, log_scale=False):
    """Plot donation time series for a specific party."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    if len(data) == 0:
        print(f"  Warning: No data for {party_name} donations ({frequency}, {segment_name})")
        plt.close()
        return
    
    # Plot
    color = '#2E86AB' if party_name == 'Democratic' else '#A23B72'
    ax.bar(range(len(data)), data['Total_Donation'], 
           color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Formatting
    ax.set_xlabel(f'{frequency.capitalize()} Period', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Donations (USD)', fontsize=12, fontweight='bold')
    
    title = f'{party_name} Donations - {frequency.capitalize()}'
    if segment_name != 'All':
        title += f' ({segment_name} Donors)'
    if log_scale:
        title += ' [Log Scale]'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Format y-axis with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    if log_scale:
        ax.set_yscale('log')
    
    # Set x-axis labels (show every nth label to avoid crowding)
    step = max(1, len(data) // 15)
    x_positions = range(0, len(data), step)
    x_labels = data[time_col].iloc[::step].tolist()
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    # Save
    party_short = 'dem' if party_name == 'Democratic' else 'rep'
    segment_short = segment_name.lower()
    log_suffix = '_log' if log_scale else ''
    filename = f'{party_short}_donations_{frequency}_{segment_short}{log_suffix}.png'
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: {filename}")

def main():
    """Main function to generate all plots."""
    print("="*80)
    print("GENERATE DONATION TIME SERIES PLOTS")
    print("="*80)
    
    # Create output directories
    output_dir = Path('donation_time_series_plots')
    output_dir.mkdir(exist_ok=True)
    output_dir_log = Path('donation_time_series_plots_log')
    output_dir_log.mkdir(exist_ok=True)
    print(f"\nOutput directory: {output_dir}/")
    print(f"Log-scale output directory: {output_dir_log}/")
    
    # Load data
    print(f"\n[1/5] Loading aggregation data...")
    weekly_df, monthly_df = load_aggregations()
    
    if weekly_df is None or monthly_df is None:
        return
    
    print(f"  ✓ Loaded weekly data: {len(weekly_df):,} records")
    print(f"  ✓ Loaded monthly data: {len(monthly_df):,} records")
    
    segments = ['All', 'Small', 'Medium', 'Large']
    frequencies = [('weekly', 'Year_Week', weekly_df), ('monthly', 'Year_Month', monthly_df)]
    
    # Generate cumulative ratio plots
    print(f"\n[2/5] Generating cumulative ratio plots (Democratic)...")
    for freq_name, time_col, df in frequencies:
        for segment in segments:
            seg_filter = None if segment == 'All' else segment
            ratio_data = prepare_ratio_data(df, time_col, seg_filter)
            plot_ratio(ratio_data, time_col, 'Dem_Ratio', 'Democratic', 
                      freq_name, segment, output_dir)
            plot_ratio(ratio_data, time_col, 'Dem_Ratio', 'Democratic', 
                      freq_name, segment, output_dir_log, log_scale=True)
    
    print(f"\n[3/5] Generating cumulative ratio plots (Republican)...")
    for freq_name, time_col, df in frequencies:
        for segment in segments:
            seg_filter = None if segment == 'All' else segment
            ratio_data = prepare_ratio_data(df, time_col, seg_filter)
            plot_ratio(ratio_data, time_col, 'Rep_Ratio', 'Republican', 
                      freq_name, segment, output_dir)
            plot_ratio(ratio_data, time_col, 'Rep_Ratio', 'Republican', 
                      freq_name, segment, output_dir_log, log_scale=True)
    
    # Generate Democratic donation plots
    print(f"\n[4/5] Generating Democratic donation plots...")
    for freq_name, time_col, df in frequencies:
        for segment in segments:
            seg_filter = None if segment == 'All' else segment
            party_data = prepare_party_data(df, time_col, 'DEM', seg_filter)
            plot_party_donations(party_data, time_col, 'Democratic', 
                                freq_name, segment, output_dir)
            plot_party_donations(party_data, time_col, 'Democratic', 
                                freq_name, segment, output_dir_log, log_scale=True)
    
    # Generate Republican donation plots
    print(f"\n[5/5] Generating Republican donation plots...")
    for freq_name, time_col, df in frequencies:
        for segment in segments:
            seg_filter = None if segment == 'All' else segment
            party_data = prepare_party_data(df, time_col, 'REP', seg_filter)
            plot_party_donations(party_data, time_col, 'Republican', 
                                freq_name, segment, output_dir)
            plot_party_donations(party_data, time_col, 'Republican', 
                                freq_name, segment, output_dir_log, log_scale=True)
    
    # Generate summary statistics
    print(f"\n{'='*80}")
    print("GENERATING SUMMARY STATISTICS")
    print(f"{'='*80}\n")
    
    summary_data = []
    
    for freq_name, time_col, df in frequencies:
        for segment in segments:
            seg_filter = None if segment == 'All' else segment
            
            # Get ratio data
            ratio_data = prepare_ratio_data(df, time_col, seg_filter)
            
            # Calculate statistics
            if len(ratio_data) > 0:
                summary_data.append({
                    'Frequency': freq_name.capitalize(),
                    'Segment': segment,
                    'Metric': 'Dem Ratio Mean',
                    'Value': ratio_data['Dem_Ratio'].mean()
                })
                summary_data.append({
                    'Frequency': freq_name.capitalize(),
                    'Segment': segment,
                    'Metric': 'Dem Ratio Median',
                    'Value': ratio_data['Dem_Ratio'].median()
                })
                summary_data.append({
                    'Frequency': freq_name.capitalize(),
                    'Segment': segment,
                    'Metric': 'Rep Ratio Mean',
                    'Value': ratio_data['Rep_Ratio'].mean()
                })
                summary_data.append({
                    'Frequency': freq_name.capitalize(),
                    'Segment': segment,
                    'Metric': 'Rep Ratio Median',
                    'Value': ratio_data['Rep_Ratio'].median()
                })
                summary_data.append({
                    'Frequency': freq_name.capitalize(),
                    'Segment': segment,
                    'Metric': 'Total Dem Donations',
                    'Value': ratio_data['DEM'].sum()
                })
                summary_data.append({
                    'Frequency': freq_name.capitalize(),
                    'Segment': segment,
                    'Metric': 'Total Rep Donations',
                    'Value': ratio_data['REP'].sum()
                })
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = output_dir / 'donation_time_series_summary.csv'
    summary_df.to_csv(summary_file, index=False)
    print(f"  ✓ Saved summary statistics to {summary_file}")
    
    print(f"\n{'='*80}")
    print(f"✓ Generated all plots successfully!")
    print(f"✓ Total plots created: 64")
    print(f"✓ Location: {output_dir}/")
    print(f"✓ Log-scale location: {output_dir_log}/")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
