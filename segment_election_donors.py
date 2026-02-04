#!/usr/bin/env python3
"""
Segment election donors into Small, Medium, and Large categories
based on cumulative donation amounts using percentile thresholds.
"""

import pandas as pd
from pathlib import Path

def main():
    """Main function to segment election donors."""
    print("="*80)
    print("SEGMENT ELECTION DONORS")
    print("="*80)
    
    # Input file
    input_file = Path('Filtered_US_Election_Donation.csv')
    
    if not input_file.exists():
        # Try alternative file name
        input_file = Path('US_Election_Donation.csv')
        if not input_file.exists():
            print("✗ Error: No donation file found. Expected Filtered_US_Election_Donation.csv or US_Election_Donation.csv")
            return
    
    print(f"\n[1/4] Loading donation data from {input_file.name}...")
    
    # Load donation data
    try:
        df = pd.read_csv(input_file, low_memory=False)
        print(f"  ✓ Loaded {len(df):,} donation records")
    except Exception as e:
        print(f"  ✗ Error loading file: {e}")
        return
    
    # Check required columns
    required_columns = ['Donator', 'Donation_Amount_USD']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"  ✗ Missing required columns: {', '.join(missing_columns)}")
        return
    
    print(f"\n[2/4] Calculating cumulative donations per donor...")
    
    # Group by Donator and calculate cumulative donation
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
    
    total_donors = len(donor_stats)
    print(f"  ✓ Found {total_donors:,} unique donors with donations")
    
    print(f"\n[3/4] Calculating percentile thresholds...")
    
    # Calculate percentile thresholds
    p33_3 = donor_stats['Cumulative_Donation_USD'].quantile(0.333)
    p66_6 = donor_stats['Cumulative_Donation_USD'].quantile(0.666)
    
    print(f"  ✓ 33.3rd percentile threshold: ${p33_3:,.2f}")
    print(f"  ✓ 66.6th percentile threshold: ${p66_6:,.2f}")
    
    print(f"\n[4/4] Classifying donors into segments...")
    
    # Classify donors into segments
    def classify_segment(cumulative_donation):
        if cumulative_donation <= p33_3:
            return 'Small'
        elif cumulative_donation <= p66_6:
            return 'Medium'
        else:
            return 'Large'
    
    donor_stats['Donor_Segment'] = donor_stats['Cumulative_Donation_USD'].apply(classify_segment)
    
    # Sort by cumulative donation (descending)
    donor_stats = donor_stats.sort_values('Cumulative_Donation_USD', ascending=False)
    
    # Save output
    output_file = Path('donor_segments.csv')
    donor_stats.to_csv(output_file, index=False)
    
    print(f"  ✓ Saved results to {output_file.name}")
    
    # Generate summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}\n")
    
    print(f"Total Donors: {total_donors:,}")
    print(f"\nPercentile Thresholds:")
    print(f"  33.3rd percentile: ${p33_3:,.2f}")
    print(f"  66.6th percentile: ${p66_6:,.2f}")
    
    print(f"\nSegment Distribution:")
    segment_counts = donor_stats['Donor_Segment'].value_counts()
    segment_totals = donor_stats.groupby('Donor_Segment')['Cumulative_Donation_USD'].sum()
    
    for segment in ['Small', 'Medium', 'Large']:
        count = segment_counts.get(segment, 0)
        pct = (count / total_donors * 100) if total_donors > 0 else 0
        total_donated = segment_totals.get(segment, 0)
        avg_donation = (total_donated / count) if count > 0 else 0
        
        print(f"  {segment:6s} Donors:")
        print(f"    Count: {count:6,} ({pct:5.2f}%)")
        print(f"    Total Donated: ${total_donated:>15,.2f}")
        print(f"    Average per Donor: ${avg_donation:>12,.2f}")
    
    # Overall statistics
    total_donated = donor_stats['Cumulative_Donation_USD'].sum()
    avg_donation = donor_stats['Cumulative_Donation_USD'].mean()
    median_donation = donor_stats['Cumulative_Donation_USD'].median()
    
    print(f"\nOverall Statistics:")
    print(f"  Total Donated: ${total_donated:,.2f}")
    print(f"  Average Donation: ${avg_donation:,.2f}")
    print(f"  Median Donation: ${median_donation:,.2f}")
    print(f"  Min Donation: ${donor_stats['Cumulative_Donation_USD'].min():,.2f}")
    print(f"  Max Donation: ${donor_stats['Cumulative_Donation_USD'].max():,.2f}")
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Segmented {total_donors:,} donors")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
