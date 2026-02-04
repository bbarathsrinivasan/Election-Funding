#!/usr/bin/env python3
"""
Build segment aggregation data and generate comparison graphs.
Step 2: Aggregate positions by segment and create comparison visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

def load_segment_mapping():
    """Load user segment mapping from all_users_analysis.csv."""
    mapping_file = Path('all_users_analysis.csv')
    
    if not mapping_file.exists():
        print("Error: all_users_analysis.csv not found. Run segment_users.py first.")
        return None
    
    df = pd.read_csv(mapping_file)
    return df.set_index('user_id')['user_segment'].to_dict()

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

def load_price_odds(event_id, market_slug, data_dir):
    """Load end-of-day YES prices and convert to day_offset."""
    price_file = data_dir / event_id / 'prices' / f'{market_slug}_price.csv'
    
    if not price_file.exists():
        return None
    
    # Load price file
    price_df = pd.read_csv(price_file)
    price_df['date'] = pd.to_datetime(price_df['timestamp'], unit='s').dt.date
    
    # Get closing date
    closing_date = load_market_closing_date(event_id, market_slug, data_dir)
    if closing_date is None:
        return None
    
    # Map token_id to token_type using trades
    trades_file = data_dir / event_id / 'trades' / f'{market_slug}_trades.csv'
    if not trades_file.exists():
        return None
    
    trades_df = pd.read_csv(trades_file)
    token_mapping = trades_df[['asset', 'outcome']].drop_duplicates()
    token_mapping['token_type'] = token_mapping['outcome'].map({'Yes': 'YES', 'No': 'NO'})
    
    price_df = price_df.merge(
        token_mapping[['asset', 'token_type']],
        left_on='token_id',
        right_on='asset',
        how='left'
    )
    
    # Filter YES tokens only
    yes_prices = price_df[price_df['token_type'] == 'YES'].copy()
    
    # Get end-of-day price (last price per day by timestamp)
    end_of_day_prices = yes_prices.sort_values('timestamp').groupby('date')['price'].last().reset_index()
    
    # Calculate day_offset
    end_of_day_prices['day_offset'] = (end_of_day_prices['date'] - closing_date).apply(lambda x: x.days)
    
    # Filter day_offset <= 0 (up to closing date)
    end_of_day_prices = end_of_day_prices[end_of_day_prices['day_offset'] <= 0]
    
    return end_of_day_prices[['day_offset', 'price']].set_index('day_offset')['price'].to_dict()

def aggregate_segment_positions(positions_dir, segment_mapping, segment_filter=None):
    """Aggregate positions for a specific segment."""
    results = []
    
    # Process all user position files
    for user_file in positions_dir.glob('user_*.csv'):
        user_id = user_file.stem.replace('user_', '')
        
        # Check if user has segment mapping
        if user_id not in segment_mapping:
            continue
        
        user_segment = segment_mapping[user_id]
        
        # Filter by segment if specified
        if segment_filter is not None and user_segment != segment_filter:
            continue
        
        # Load user positions
        df = pd.read_csv(user_file)
        
        # Filter users with non-zero cumulative positions
        df = df[(df['yes_cumulative_position'] != 0) | (df['no_cumulative_position'] != 0)]
        
        if df.empty:
            continue
        
        # Aggregate by day_offset
        for day_offset, group in df.groupby('day_offset'):
            # Sum individual positions only where corresponding cumulative position != 0
            agg_yes = group[group['yes_cumulative_position'] != 0]['individual_yes_position'].sum()
            agg_no = group[group['no_cumulative_position'] != 0]['individual_no_position'].sum()
            
            results.append({
                'day_offset': day_offset,
                'agg_yes': agg_yes,
                'agg_no': agg_no,
            })
    
    if not results:
        return None
    
    result_df = pd.DataFrame(results)
    # Aggregate across all users for each day_offset
    result_df = result_df.groupby('day_offset').agg({
        'agg_yes': 'sum',
        'agg_no': 'sum',
    }).reset_index()
    
    # Calculate odds
    total = result_df['agg_yes'] + result_df['agg_no']
    result_df['odds'] = result_df['agg_yes'] / total
    result_df.loc[total == 0, 'odds'] = np.nan
    
    return result_df.sort_values('day_offset')

def process_market(event_id, market_slug, data_dir, segment_mapping, market_num, total_markets):
    """Process a single market and generate segment aggregations and graph."""
    print(f"  [{market_num}/{total_markets}] Processing {market_slug}...")
    
    positions_dir = Path('data_segment_output') / event_id / market_slug
    
    if not positions_dir.exists():
        print(f"  Warning: No positions data found for {market_slug}")
        return
    
    # Create output directory
    output_dir = Path('data_segment') / event_id / market_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Aggregate by segment
    all_segments = aggregate_segment_positions(positions_dir, segment_mapping)
    small_segment = aggregate_segment_positions(positions_dir, segment_mapping, 'Small')
    medium_segment = aggregate_segment_positions(positions_dir, segment_mapping, 'Medium')
    large_segment = aggregate_segment_positions(positions_dir, segment_mapping, 'Large')
    
    # Load price odds
    price_odds = load_price_odds(event_id, market_slug, data_dir)
    
    # Save CSV files
    if all_segments is not None:
        all_segments.to_csv(output_dir / 'all_segments.csv', index=False)
    
    if small_segment is not None:
        small_segment.to_csv(output_dir / 'small_segment.csv', index=False)
    
    if medium_segment is not None:
        medium_segment.to_csv(output_dir / 'medium_segment.csv', index=False)
    
    if large_segment is not None:
        large_segment.to_csv(output_dir / 'large_segment.csv', index=False)
    
    # Create comparison graph
    plt.figure(figsize=(12, 8))
    
    # Plot price-based market odds (blue)
    if price_odds:
        price_day_offsets = sorted(price_odds.keys())
        price_values = [price_odds[d] for d in price_day_offsets]
        plt.plot(price_day_offsets, price_values, 'b-o', label='Price-based Market Odds', linewidth=2, markersize=4)
    
    # Plot investment-based odds
    if all_segments is not None:
        plt.plot(all_segments['day_offset'], all_segments['odds'], 'g-s', label='All Segments', linewidth=2, markersize=4)
    
    if small_segment is not None:
        plt.plot(small_segment['day_offset'], small_segment['odds'], 'orange', marker='^', label='Small Segment', linewidth=2, markersize=4)
    
    if medium_segment is not None:
        plt.plot(medium_segment['day_offset'], medium_segment['odds'], 'r-D', label='Medium Segment', linewidth=2, markersize=4)
    
    if large_segment is not None:
        plt.plot(large_segment['day_offset'], large_segment['odds'], 'purple', marker='*', label='Large Segment', linewidth=2, markersize=4)
    
    plt.xlabel('Day Offset (0 = closing day)', fontsize=12)
    plt.ylabel('Odds', fontsize=12)
    plt.title(f'Odds Comparison: Investment-based vs Market-based\n{market_slug}', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xlim(left=None)  # Let matplotlib auto-scale
    plt.ylim(0, 1)
    
    # Save graph
    graph_file = output_dir / 'odds_comparison.png'
    plt.savefig(graph_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"    ✓ Created CSV files and comparison graph")

def main():
    """Main function to process all markets."""
    print("="*80)
    print("BUILD SEGMENT AGGREGATION - Step 3")
    print("="*80)
    
    # Load segment mapping
    print("\n[1/3] Loading segment mapping...")
    segment_mapping = load_segment_mapping()
    if segment_mapping is None:
        return
    print(f"  ✓ Loaded segment mapping for {len(segment_mapping)} users")
    
    data_dir = Path('data')
    
    if not data_dir.exists():
        print("✗ Error: data directory not found.")
        return
    
    # Collect all markets first
    print(f"\n[2/3] Scanning for markets...")
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
            all_markets.append((event_id, market_slug))
    
    total_markets = len(all_markets)
    print(f"  ✓ Found {total_markets} markets to process")
    
    # Process all markets
    print(f"\n[3/3] Processing markets and generating graphs...")
    for market_num, (event_id, market_slug) in enumerate(all_markets, 1):
        try:
            process_market(event_id, market_slug, data_dir, segment_mapping, market_num, total_markets)
        except Exception as e:
            print(f"  ✗ Error processing {market_slug}: {e}")
            continue
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Processed {total_markets} markets, generated CSV files and comparison graphs")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

