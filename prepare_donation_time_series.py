#!/usr/bin/env python3
"""
Prepare donation time series data for visualization.
Processes ~70M donation records and creates weekly/monthly aggregations
by party and donor segment.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def parse_date(date_str):
    """
    Parse date from MMDDYYYY format (e.g., 7312023 = July 31, 2023)
    Handles various formats including MDDYYYY, MMDDYYYY, etc.
    """
    if pd.isna(date_str):
        return pd.NaT
    
    date_str = str(int(date_str))
    
    # Pad to ensure we have at least 7 digits (MDDYYYY)
    if len(date_str) < 7:
        return pd.NaT
    
    try:
        # Try MMDDYYYY format (8 digits)
        if len(date_str) == 8:
            month = int(date_str[:2])
            day = int(date_str[2:4])
            year = int(date_str[4:])
        # Try MDDYYYY format (7 digits)
        elif len(date_str) == 7:
            month = int(date_str[0])
            day = int(date_str[1:3])
            year = int(date_str[3:])
        else:
            return pd.NaT
        
        return pd.Timestamp(year=year, month=month, day=day)
    except:
        return pd.NaT

def main():
    """Main function to prepare time series data."""
    print("="*80)
    print("PREPARE DONATION TIME SERIES DATA")
    print("="*80)
    
    # Input files
    donation_file = Path('US_Election_Donation.csv')
    segment_file = Path('donor_segments.csv')
    
    # Check files exist
    if not donation_file.exists():
        print(f"✗ Error: {donation_file} not found")
        return
    if not segment_file.exists():
        print(f"✗ Error: {segment_file} not found")
        print("  Run segment_election_donors.py first to create donor segments")
        return
    
    print(f"\n[1/5] Loading donor segments...")
    segments_df = pd.read_csv(segment_file)
    print(f"  ✓ Loaded {len(segments_df):,} donor segments")
    
    # Create a dictionary for fast lookup
    donor_segments = dict(zip(segments_df['Donator'], segments_df['Donor_Segment']))
    
    print(f"\n[2/5] Processing donation data in chunks...")
    print(f"  Reading from: {donation_file}")
    
    # Process in chunks to handle large file
    chunk_size = 1_000_000
    all_processed = []
    total_processed = 0
    total_skipped = 0
    
    chunk_iter = pd.read_csv(donation_file, chunksize=chunk_size, low_memory=False)
    
    for chunk_num, chunk in enumerate(chunk_iter, 1):
        # Filter for only DEM and REP parties
        chunk = chunk[chunk['Party'].isin(['DEM', 'REP'])].copy()
        
        # Parse dates
        chunk['Date'] = chunk['Received'].apply(parse_date)
        
        # Filter out invalid dates and amounts
        chunk = chunk[chunk['Date'].notna()].copy()
        chunk['Donation_Amount_USD'] = pd.to_numeric(chunk['Donation_Amount_USD'], errors='coerce')
        chunk = chunk[chunk['Donation_Amount_USD'] > 0].copy()
        
        # Add donor segment
        chunk['Donor_Segment'] = chunk['Donator'].map(donor_segments)
        
        # Keep only donors with segments
        before_filter = len(chunk)
        chunk = chunk[chunk['Donor_Segment'].notna()].copy()
        skipped = before_filter - len(chunk)
        total_skipped += skipped
        
        if len(chunk) > 0:
            # Ensure Date column is datetime type
            chunk['Date'] = pd.to_datetime(chunk['Date'])
            
            # Extract week and month
            chunk['Year'] = chunk['Date'].dt.year
            chunk['Week'] = chunk['Date'].dt.isocalendar().week
            chunk['Month'] = chunk['Date'].dt.month
            chunk['Year_Week'] = chunk['Year'].astype(str) + '-W' + chunk['Week'].astype(str).str.zfill(2)
            chunk['Year_Month'] = chunk['Date'].dt.to_period('M').astype(str)
            
            # Keep only needed columns
            chunk = chunk[['Party', 'Donator', 'Donation_Amount_USD', 'Donor_Segment', 
                          'Date', 'Year_Week', 'Year_Month']].copy()
            
            all_processed.append(chunk)
            total_processed += len(chunk)
        
        if chunk_num % 10 == 0:
            print(f"  Processed {chunk_num * chunk_size:,} records... "
                  f"(kept: {total_processed:,}, skipped: {total_skipped:,})")
    
    print(f"\n  ✓ Total processed: {total_processed:,} records")
    print(f"  ✓ Skipped (no segment): {total_skipped:,} records")
    
    if not all_processed:
        print("✗ Error: No valid data to process")
        return
    
    print(f"\n[3/5] Combining processed chunks...")
    df = pd.concat(all_processed, ignore_index=True)
    print(f"  ✓ Combined {len(df):,} records")
    
    # Save intermediate processed data
    print(f"\n[4/5] Saving processed data...")
    output_dir = Path('donation_time_series_data')
    output_dir.mkdir(exist_ok=True)
    
    processed_file = output_dir / 'processed_donations.csv'
    df.to_csv(processed_file, index=False)
    print(f"  ✓ Saved to {processed_file}")
    
    print(f"\n[5/5] Creating aggregations...")
    
    # Weekly aggregations by segment and party
    weekly_agg = df.groupby(['Year_Week', 'Donor_Segment', 'Party'])['Donation_Amount_USD'].sum().reset_index()
    weekly_agg.columns = ['Year_Week', 'Donor_Segment', 'Party', 'Total_Donation']
    
    # Monthly aggregations by segment and party
    monthly_agg = df.groupby(['Year_Month', 'Donor_Segment', 'Party'])['Donation_Amount_USD'].sum().reset_index()
    monthly_agg.columns = ['Year_Month', 'Donor_Segment', 'Party', 'Total_Donation']
    
    # Save aggregations
    weekly_file = output_dir / 'weekly_aggregations.csv'
    monthly_file = output_dir / 'monthly_aggregations.csv'
    
    weekly_agg.to_csv(weekly_file, index=False)
    monthly_agg.to_csv(monthly_file, index=False)
    
    print(f"  ✓ Weekly aggregations: {weekly_file}")
    print(f"  ✓ Monthly aggregations: {monthly_file}")
    
    # Generate summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}\n")
    
    print(f"Total donations processed: {len(df):,}")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"\nDonations by Party:")
    party_summary = df.groupby('Party')['Donation_Amount_USD'].agg(['sum', 'count'])
    for party in party_summary.index:
        total = party_summary.loc[party, 'sum']
        count = party_summary.loc[party, 'count']
        print(f"  {party}: ${total:,.2f} ({count:,} donations)")
    
    print(f"\nDonations by Segment:")
    segment_summary = df.groupby('Donor_Segment')['Donation_Amount_USD'].agg(['sum', 'count'])
    for segment in ['Small', 'Medium', 'Large']:
        if segment in segment_summary.index:
            total = segment_summary.loc[segment, 'sum']
            count = segment_summary.loc[segment, 'count']
            print(f"  {segment}: ${total:,.2f} ({count:,} donations)")
    
    print(f"\nUnique donors: {df['Donator'].nunique():,}")
    print(f"Unique weeks: {df['Year_Week'].nunique()}")
    print(f"Unique months: {df['Year_Month'].nunique()}")
    
    print(f"\n{'='*80}")
    print("✓ Data preparation complete!")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
