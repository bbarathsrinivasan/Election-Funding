#!/usr/bin/env python3
"""
Build segment positions data from trades.
Step 1: Process trades and create per-user position files with day_offset.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def load_market_closing_date(event_id, market_slug, data_dir):
    """Load closing date from meta file."""
    meta_file = data_dir / event_id / 'meta' / f'meta_{event_id}.csv'
    
    if not meta_file.exists():
        return None
    
    meta_df = pd.read_csv(meta_file)
    market_meta = meta_df[meta_df['market_slug'] == market_slug]
    
    if market_meta.empty:
        return None
    
    closing_date_str = market_meta['market_endDate'].iloc[0]
    closing_date = pd.to_datetime(closing_date_str).date()
    
    return closing_date

def process_market_trades(trades_file, event_id, market_slug, data_dir, market_num, total_markets):
    """Process trades for a single market and generate user position files."""
    print(f"  [{market_num}/{total_markets}] Processing {market_slug}...")
    
    # Load trades
    df = pd.read_csv(trades_file)
    
    # Map columns
    df['user_id'] = df['proxyWallet']
    df['token_type'] = df['outcome'].map({'Yes': 'YES', 'No': 'NO'})
    
    # Convert timestamp to date
    df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
    
    # Get closing date
    closing_date = load_market_closing_date(event_id, market_slug, data_dir)
    if closing_date is None:
        print(f"  Warning: Could not find closing date for {market_slug}, skipping...")
        return
    
    # Calculate day_offset
    df['day_offset'] = (df['date'] - closing_date).apply(lambda x: x.days)
    
    # Calculate net tokens per trade
    df['net_tokens'] = df.apply(
        lambda row: row['size'] if row['side'] == 'BUY' else -row['size'],
        axis=1
    )
    
    # Group by user_id, day_offset, and token_type
    grouped = df.groupby(['user_id', 'day_offset', 'token_type'])['net_tokens'].sum().reset_index()
    
    # Pivot to get yes_net_tokens and no_net_tokens
    pivoted = grouped.pivot_table(
        index=['user_id', 'day_offset'],
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
    
    # Process each user
    output_dir = Path('data_segment_output') / event_id / market_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    
    unique_users = pivoted['user_id'].unique()
    total_users = len(unique_users)
    
    for user_idx, (user_id, user_data) in enumerate(pivoted.groupby('user_id'), 1):
        # Sort by day_offset (ascending, from earliest to latest)
        user_data = user_data.sort_values('day_offset').copy()
        
        # Calculate cumulative positions
        user_data['yes_cumulative_position'] = user_data['yes_net_tokens'].cumsum()
        user_data['no_cumulative_position'] = user_data['no_net_tokens'].cumsum()
        
        # Calculate individual positions
        # H_y = yes_cumulative_position, H_n = no_cumulative_position
        H_y = user_data['yes_cumulative_position']
        H_n = user_data['no_cumulative_position']
        
        user_data['individual_yes_position'] = (
            (H_y * (H_y > 0)) + (-H_n * (H_n < 0))
        )
        user_data['individual_no_position'] = (
            (H_n * (H_n > 0)) + (-H_y * (H_y < 0))
        )
        
        # Try to load prices (optional)
        price_file = data_dir / event_id / 'prices' / f'{market_slug}_price.csv'
        yes_prices = {}
        no_prices = {}
        
        if price_file.exists():
            try:
                price_df = pd.read_csv(price_file)
                price_df['date'] = pd.to_datetime(price_df['timestamp'], unit='s').dt.date
                
                # Map token_id to token_type using trades
                token_mapping = df[['asset', 'outcome']].drop_duplicates()
                token_mapping['token_type'] = token_mapping['outcome'].map({'Yes': 'YES', 'No': 'NO'})
                
                price_df = price_df.merge(
                    token_mapping[['asset', 'token_type']],
                    left_on='token_id',
                    right_on='asset',
                    how='left'
                )
                
                # Get end-of-day prices per date
                for date, group in price_df.groupby('date'):
                    day_offset = (date - closing_date).days
                    yes_price = group[group['token_type'] == 'YES']['price'].iloc[-1] if len(group[group['token_type'] == 'YES']) > 0 else None
                    no_price = group[group['token_type'] == 'NO']['price'].iloc[-1] if len(group[group['token_type'] == 'NO']) > 0 else None
                    
                    if yes_price is not None:
                        yes_prices[day_offset] = yes_price
                    if no_price is not None:
                        no_prices[day_offset] = no_price
            except Exception as e:
                print(f"  Warning: Could not load prices: {e}")
        
        # Add prices to user data
        user_data['yes_price'] = user_data['day_offset'].map(yes_prices)
        user_data['no_price'] = user_data['day_offset'].map(no_prices)
        
        # Select and reorder columns
        output_df = user_data[[
            'user_id', 'day_offset', 'yes_cumulative_position', 'no_cumulative_position',
            'individual_yes_position', 'individual_no_position', 'yes_price', 'no_price'
        ]].copy()
        
        # Write to file
        output_file = output_dir / f'user_{user_id}.csv'
        output_df.to_csv(output_file, index=False)
    
    print(f"    ✓ Created {total_users} user position files")

def main():
    """Main function to process all markets."""
    print("="*80)
    print("BUILD SEGMENT POSITIONS - Step 2")
    print("="*80)
    
    data_dir = Path('data')
    
    if not data_dir.exists():
        print("✗ Error: data directory not found.")
        return
    
    # Collect all markets first
    print("\n[1/2] Scanning for markets...")
    all_markets = []
    for event_dir in data_dir.iterdir():
        if not event_dir.is_dir():
            continue
        
        event_id = event_dir.name
        trades_dir = event_dir / 'trades'
        
        if not trades_dir.exists():
            continue
        
        for trades_file in trades_dir.glob('*_trades.csv'):
            market_slug = trades_file.stem.replace('_trades', '')
            all_markets.append((trades_file, event_id, market_slug))
    
    total_markets = len(all_markets)
    print(f"  ✓ Found {total_markets} markets to process")
    
    # Process all trades files
    print(f"\n[2/2] Processing markets...")
    for market_num, (trades_file, event_id, market_slug) in enumerate(all_markets, 1):
        try:
            process_market_trades(trades_file, event_id, market_slug, data_dir, market_num, total_markets)
        except Exception as e:
            print(f"  ✗ Error processing {market_slug}: {e}")
            continue
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Processed {total_markets} markets")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

