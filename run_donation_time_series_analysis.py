#!/usr/bin/env python3
"""
Master orchestration script for donation time series analysis.
Runs both data preparation and visualization in sequence.
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"{'='*80}\n")
    
    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print(f"\n✗ Error running {script_name}")
        return False
    
    print(f"\n✓ {description} completed successfully")
    return True

def main():
    """Main orchestration function."""
    print("="*80)
    print("DONATION TIME SERIES ANALYSIS - MASTER ORCHESTRATION")
    print("="*80)
    print("\nThis will:")
    print("  1. Process ~70M donation records")
    print("  2. Create weekly/monthly aggregations")
    print("  3. Generate 32 visualization plots")
    print("\n⏱ Estimated time: 10-20 minutes depending on system performance")
    print("="*80)
    
    # Step 1: Data preparation
    if not run_script('prepare_donation_time_series.py', 'Data Preparation'):
        return
    
    # Step 2: Visualization
    if not run_script('plot_donation_time_series.py', 'Visualization Generation'):
        return
    
    print("\n" + "="*80)
    print("✓ ALL TASKS COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nGenerated files:")
    print("  • donation_time_series_data/ - Processed data and aggregations")
    print("  • donation_time_series_plots/ - 32 visualization plots")
    print("  • donation_time_series_plots/donation_time_series_summary.csv - Summary statistics")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
