#!/usr/bin/env python3
"""
Generate combined_token.csv files from trades data.
Processes trades and calculates daily net tokens per user, market, and date.
"""

import pandas as pd
import os
from pathlib import Path
from collections import defaultdict

def process_trades_file(trades_file, event_id):
    """Process a single trades file and return aggregated data."""
    print(f"Processing {trades_file}...")
    
    # Read trades file
    df = pd.read_csv(trades_file)
    
    # Map columns
    df['user_id'] = df['proxyWallet']
    df['token_type'] = df['outcome'].map({'Yes': 'YES', 'No': 'NO'})
    
    # Convert timestamp to date
    df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
    
    # Get market_slug from the filename or slug column
    market_slug = df['slug'].iloc[0] if 'slug' in df.columns else Path(trades_file).stem.replace('_trades', '')
    
    # Calculate net tokens per day
    # BUY increases position (positive), SELL decreases position (negative)
    df['net_tokens'] = df.apply(
        lambda row: row['size'] if row['side'] == 'BUY' else -row['size'],
        axis=1
    )
    
    # Group by user_id, date, and token_type
    grouped = df.groupby(['user_id', 'date', 'token_type'])['net_tokens'].sum().reset_index()
    
    # Pivot to get yes_net_tokens and no_net_tokens
    pivoted = grouped.pivot_table(
        index=['user_id', 'date'],
        columns='token_type',
        values='net_tokens',
        fill_value=0
    ).reset_index()
    
    # Rename columns
    if 'YES' in pivoted.columns:
        pivoted['yes_net_tokens'] = pivoted['YES']
    else:
        pivoted['yes_net_tokens'] = 0
    
    if 'NO' in pivoted.columns:
        pivoted['no_net_tokens'] = pivoted['NO']
    else:
        pivoted['no_net_tokens'] = 0
    
    # Add event_id and market_slug
    pivoted['event_id'] = event_id
    pivoted['market_slug'] = market_slug
    
    # Select and reorder columns
    result = pivoted[['user_id', 'event_id', 'market_slug', 'date', 'yes_net_tokens', 'no_net_tokens']].copy()
    
    return result

def main():
    """Main function to process all trades files."""
    print("="*80)
    print("BUILD COMBINED TOKEN - Step 0a")
    print("="*80)
    
    data_dir = Path('data')
    output_dir = Path('combined_token_output')
    
    # Dictionary to store data per user per event
    user_event_data = defaultdict(lambda: defaultdict(list))
    
    # Collect all trades files first
    print("\n[1/2] Scanning for trades files...")
    all_trades_files = []
    for event_dir in data_dir.iterdir():
        if not event_dir.is_dir():
            continue
        
        event_id = event_dir.name
        trades_dir = event_dir / 'trades'
        
        if not trades_dir.exists():
            print(f"  ⚠ No trades directory found for {event_id}")
            continue
        
        trades_files = list(trades_dir.glob('*_trades.csv'))
        all_trades_files.extend([(f, event_id) for f in trades_files])
    
    total_files = len(all_trades_files)
    print(f"  ✓ Found {total_files} trades files to process")
    
    # Process all trades files
    print(f"\n[2/2] Processing trades files...")
    for idx, (trades_file, event_id) in enumerate(all_trades_files, 1):
        if idx % 10 == 0 or idx == total_files:
            print(f"  Progress: {idx}/{total_files} files ({idx*100//total_files}%)")
        
        try:
            result_df = process_trades_file(trades_file, event_id)
            
            # Group by user_id and append to user_event_data
            for user_id, group in result_df.groupby('user_id'):
                user_event_data[event_id][user_id].append(group)
                
        except Exception as e:
            print(f"  ✗ Error processing {trades_file.name}: {e}")
            continue
    
    # Write output files per user per event
    print(f"\n[3/3] Writing output files...")
    total_users = sum(len(users) for users in user_event_data.values())
    user_count = 0
    
    for event_id, user_data in user_event_data.items():
        for user_id, dataframes in user_data.items():
            user_count += 1
            if user_count % 100 == 0 or user_count == total_users:
                print(f"  Progress: {user_count}/{total_users} users ({user_count*100//total_users}%)")
            
            # Combine all dataframes for this user in this event
            combined_df = pd.concat(dataframes, ignore_index=True)
            
            # Sort by market_slug, date
            combined_df = combined_df.sort_values(['market_slug', 'date'])
            
            # Create output directory
            user_output_dir = output_dir / event_id / f'user_{user_id}'
            user_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            output_file = user_output_dir / 'combined_token.csv'
            combined_df.to_csv(output_file, index=False)
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Processed {total_files} trades files, created {total_users} user files")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

