#!/usr/bin/env python3
"""
Generate date_group_token.csv files with value calculations.
Calculates yes_value and no_value by multiplying net_tokens with closing prices.
"""

import pandas as pd
import os
from pathlib import Path
from collections import defaultdict

def load_closing_prices(event_id, market_slug, data_dir):
    """Load closing prices for a market. Try _closing_prices.csv first, then generate from _price.csv."""
    prices_dir = data_dir / event_id / 'prices'
    
    # Try to load _closing_prices.csv first
    closing_prices_file = prices_dir / f'{market_slug}_closing_prices.csv'
    if closing_prices_file.exists():
        df = pd.read_csv(closing_prices_file)
        df['date'] = pd.to_datetime(df['date']).dt.date
        return df
    
    # Otherwise, generate from _price.csv
    price_file = prices_dir / f'{market_slug}_price.csv'
    if not price_file.exists():
        return None
    
    # Load price file
    price_df = pd.read_csv(price_file)
    price_df['date'] = pd.to_datetime(price_df['timestamp'], unit='s').dt.date
    
    # Need to map token_id to token_type using trades file
    trades_file = data_dir / event_id / 'trades' / f'{market_slug}_trades.csv'
    if not trades_file.exists():
        return None
    
    trades_df = pd.read_csv(trades_file)
    # Create mapping: asset -> outcome -> token_type
    token_mapping = trades_df[['asset', 'outcome']].drop_duplicates()
    token_mapping['token_type'] = token_mapping['outcome'].map({'Yes': 'YES', 'No': 'NO'})
    
    # Merge with price data
    price_df = price_df.merge(
        token_mapping[['asset', 'token_type']],
        left_on='token_id',
        right_on='asset',
        how='left'
    )
    
    # Get last price per day per token_type
    closing_prices = price_df.groupby(['date', 'token_type'])['price'].last().reset_index()
    
    return closing_prices

def process_user_combined_token(combined_token_file, data_dir, closing_prices_cache):
    """Process a single user's combined_token.csv file."""
    user_id = combined_token_file.parent.name.replace('user_', '')
    event_id = combined_token_file.parent.parent.name
    
    # Load combined_token data
    df = pd.read_csv(combined_token_file)
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Dictionary to store results
    results = []
    
    # Process each market
    for market_slug, market_data in df.groupby('market_slug'):
        # Get closing prices from cache
        cache_key = (event_id, market_slug)
        if cache_key not in closing_prices_cache:
            closing_prices = load_closing_prices(event_id, market_slug, data_dir)
            closing_prices_cache[cache_key] = closing_prices
        else:
            closing_prices = closing_prices_cache[cache_key]
        
        if closing_prices is None:
            continue
        
        # Merge YES prices
        yes_prices = closing_prices[closing_prices['token_type'] == 'YES'][['date', 'price']].rename(columns={'price': 'yes_closing_price'})
        market_data = market_data.merge(yes_prices, on='date', how='left')
        
        # Merge NO prices
        no_prices = closing_prices[closing_prices['token_type'] == 'NO'][['date', 'price']].rename(columns={'price': 'no_closing_price'})
        market_data = market_data.merge(no_prices, on='date', how='left')
        
        # Calculate values using vectorized operations
        market_data['yes_value'] = market_data['yes_net_tokens'] * market_data['yes_closing_price'].fillna(0)
        market_data['no_value'] = market_data['no_net_tokens'] * market_data['no_closing_price'].fillna(0)
        
        # Convert to list of dicts (much faster than iterrows)
        market_data['user_id'] = user_id
        market_data['event_id'] = event_id
        results.extend(market_data[['user_id', 'event_id', 'market_slug', 'date', 'yes_net_tokens', 'no_net_tokens', 'yes_value', 'no_value']].to_dict('records'))
    
    return results

def main():
    """Main function to process all combined_token files."""
    combined_token_dir = Path('combined_token_output')
    data_dir = Path('data')
    output_dir = Path('date_group_token_output')
    
    if not combined_token_dir.exists():
        print("Error: combined_token_output directory not found. Run build_combined_token.py first.")
        return
    
    # Cache for closing prices (load once per market, not per user)
    closing_prices_cache = {}
    
    # Dictionary to store data per user (across all events)
    user_data = defaultdict(list)
    
    # Collect all files first
    all_files = []
    for event_dir in combined_token_dir.iterdir():
        if not event_dir.is_dir():
            continue
        
        event_id = event_dir.name
        user_dirs = [d for d in event_dir.iterdir() if d.is_dir() and d.name.startswith('user_')]
        
        for user_dir in user_dirs:
            combined_token_file = user_dir / 'combined_token.csv'
            if combined_token_file.exists():
                all_files.append((combined_token_file, event_id))
    
    print("="*80)
    print("BUILD DATE GROUP TOKEN - Step 0b")
    print("="*80)
    print(f"\n[1/2] Processing {len(all_files)} user files...")
    
    # Process all files
    for idx, (combined_token_file, event_id) in enumerate(all_files, 1):
        if idx % 100 == 0 or idx == len(all_files):
            remaining = len(all_files) - idx
            pct = idx * 100 // len(all_files)
            print(f"  Progress: {idx}/{len(all_files)} users ({pct}%) - {remaining} remaining")
        
        try:
            results = process_user_combined_token(combined_token_file, data_dir, closing_prices_cache)
            # Extract user_id from directory name (user_<user_id>)
            user_id = combined_token_file.parent.name.replace('user_', '')
            user_data[user_id].extend(results)
        except Exception as e:
            print(f"  ✗ Error processing {combined_token_file.parent.name}: {e}")
            continue
    
    print(f"  ✓ Loaded closing prices for {len(closing_prices_cache)} markets")
    
    # Aggregate by user and date (sum across all markets and events)
    print(f"\n[2/2] Aggregating by user and date...")
    total_users = len(user_data)
    user_count = 0
    
    for user_id, results in user_data.items():
        user_count += 1
        if user_count % 100 == 0 or user_count == total_users:
            remaining = total_users - user_count
            pct = user_count * 100 // total_users
            print(f"  Progress: {user_count}/{total_users} users ({pct}%) - {remaining} remaining")
        if not results:
            continue
        
        df = pd.DataFrame(results)
        
        # Group by user_id and date, sum values
        aggregated = df.groupby(['user_id', 'date']).agg({
            'yes_net_tokens': 'sum',
            'no_net_tokens': 'sum',
            'yes_value': 'sum',
            'no_value': 'sum',
        }).reset_index()
        
        # Calculate buy totals (positive net_tokens)
        aggregated['YES Buy Total'] = 0
        aggregated['NO Buy Total'] = 0
        aggregated.loc[aggregated['yes_net_tokens'] > 0, 'YES Buy Total'] = aggregated.loc[aggregated['yes_net_tokens'] > 0, 'yes_net_tokens']
        aggregated.loc[aggregated['no_net_tokens'] > 0, 'NO Buy Total'] = aggregated.loc[aggregated['no_net_tokens'] > 0, 'no_net_tokens']
        
        # Sort by date
        aggregated = aggregated.sort_values('date')
        
        # Create output directory
        user_output_dir = output_dir / f'user_{user_id}'
        user_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        output_file = user_output_dir / 'date_group_token.csv'
        aggregated.to_csv(output_file, index=False)
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Processed {total_users} users, created date_group_token.csv files")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

