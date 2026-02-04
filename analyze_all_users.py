#!/usr/bin/env python3
"""
Analyze all users and calculate cumulative_total_value_max.
Generates all_users_analysis.csv with user statistics.
"""

import pandas as pd
from pathlib import Path

def analyze_user(date_group_token_file):
    """Analyze a single user's date_group_token.csv file."""
    user_id = date_group_token_file.parent.name.replace('user_', '')
    
    # Load date_group_token data
    df = pd.read_csv(date_group_token_file)
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Calculate cumulative total value over time
    df['total_value'] = df['yes_value'] + df['no_value']
    df['cumulative_total_value'] = df['total_value'].cumsum()
    
    # Get maximum cumulative total value
    cumulative_total_value_max = df['cumulative_total_value'].max()
    
    # Calculate other statistics
    total_yes_value = df['yes_value'].sum()
    total_no_value = df['no_value'].sum()
    total_yes_net_tokens = df['yes_net_tokens'].sum()
    total_no_net_tokens = df['no_net_tokens'].sum()
    num_dates = len(df)
    first_date = df['date'].min()
    last_date = df['date'].max()
    
    return {
        'user_id': user_id,
        'cumulative_total_value_max': cumulative_total_value_max,
        'total_yes_value': total_yes_value,
        'total_no_value': total_no_value,
        'total_yes_net_tokens': total_yes_net_tokens,
        'total_no_net_tokens': total_no_net_tokens,
        'num_dates': num_dates,
        'first_date': first_date,
        'last_date': last_date,
    }

def main():
    """Main function to analyze all users."""
    print("="*80)
    print("ANALYZE ALL USERS - Step 1a")
    print("="*80)
    
    date_group_token_dir = Path('date_group_token_output')
    output_file = Path('all_users_analysis.csv')
    
    if not date_group_token_dir.exists():
        print("✗ Error: date_group_token_output directory not found. Run build_date_group_token.py first.")
        return
    
    # Collect all user files first
    print("\n[1/2] Scanning for user files...")
    all_user_files = []
    for user_dir in date_group_token_dir.iterdir():
        if not user_dir.is_dir():
            continue
        
        date_group_token_file = user_dir / 'date_group_token.csv'
        if date_group_token_file.exists():
            all_user_files.append(date_group_token_file)
    
    total_users = len(all_user_files)
    print(f"  ✓ Found {total_users} user files to analyze")
    
    # Collect all user analyses
    print(f"\n[2/2] Analyzing users...")
    user_analyses = []
    
    # Process all user directories
    for idx, date_group_token_file in enumerate(all_user_files, 1):
        if idx % 100 == 0 or idx == total_users:
            remaining = total_users - idx
            pct = idx * 100 // total_users
            print(f"  Progress: {idx}/{total_users} users ({pct}%) - {remaining} remaining")
        
        try:
            analysis = analyze_user(date_group_token_file)
            user_analyses.append(analysis)
        except Exception as e:
            print(f"  ✗ Error analyzing {date_group_token_file.parent.name}: {e}")
            continue
    
    if not user_analyses:
        print("No user data found to analyze.")
        return
    
    # Create DataFrame and save
    print(f"\n[3/3] Saving results...")
    df = pd.DataFrame(user_analyses)
    df = df.sort_values('cumulative_total_value_max', ascending=False)
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Analyzed {len(df)} users")
    print(f"\nStatistics:")
    print(f"  Large users (≥1M): {len(df[df['cumulative_total_value_max'] >= 1000000])}")
    print(f"  Medium users (10K-1M): {len(df[(df['cumulative_total_value_max'] >= 10000) & (df['cumulative_total_value_max'] < 1000000)])}")
    print(f"  Small users (<10K): {len(df[df['cumulative_total_value_max'] < 10000])}")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

