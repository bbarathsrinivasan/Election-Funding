#!/usr/bin/env python3
"""
Classify users into segments based on cumulative_total_value_max.
Updates all_users_analysis.csv with user_segment column.
"""

import pandas as pd
from pathlib import Path

def main():
    """Main function to segment users."""
    print("="*80)
    print("SEGMENT USERS - Step 1b")
    print("="*80)
    
    input_file = Path('all_users_analysis.csv')
    
    if not input_file.exists():
        print("✗ Error: all_users_analysis.csv not found. Run analyze_all_users.py first.")
        return
    
    print(f"\n[1/2] Loading user analysis...")
    # Load user analysis
    df = pd.read_csv(input_file)
    print(f"  ✓ Loaded {len(df)} users")
    
    # Classify users into segments
    print(f"\n[2/2] Classifying users into segments...")
    def classify_segment(cumulative_total_value_max):
        if cumulative_total_value_max >= 1000000:
            return 'Large'
        elif cumulative_total_value_max >= 10000:
            return 'Medium'
        else:
            return 'Small'
    
    df['user_segment'] = df['cumulative_total_value_max'].apply(classify_segment)
    
    # Save updated file
    df.to_csv(input_file, index=False)
    
    print(f"\n{'='*80}")
    print(f"✓ COMPLETED: Classified {len(df)} users into segments")
    print(f"\nSegment distribution:")
    segment_counts = df['user_segment'].value_counts()
    for segment, count in segment_counts.items():
        pct = count * 100 // len(df)
        print(f"  {segment:6s}: {count:4d} users ({pct:3d}%)")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

