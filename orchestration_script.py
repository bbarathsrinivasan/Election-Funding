#!/usr/bin/env python3
"""
Orchestration script to run all data segment pipeline scripts in order.
Executes the complete pipeline from raw trades to segment aggregations and graphs.
"""

import subprocess
import sys
from pathlib import Path
import time

def run_script(script_name, description, step_num, total_steps):
    """Run a Python script and handle errors."""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}/{total_steps}: {description}")
    print(f"Running: {script_name}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        print(f"\n{'='*80}")
        print(f"✓ STEP {step_num}/{total_steps} COMPLETED: {description}")
        print(f"  Time taken: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print(f"{'='*80}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n{'='*80}")
        print(f"✗ STEP {step_num}/{total_steps} FAILED: {description}")
        print(f"  Error: {e}")
        print(f"{'='*80}")
        return False
    except FileNotFoundError:
        print(f"\n{'='*80}")
        print(f"✗ Script not found: {script_name}")
        print(f"{'='*80}")
        return False

def main():
    """Main orchestration function."""
    print("="*80)
    print("Data Segment Pipeline - Orchestration Script")
    print("="*80)
    
    # Define the pipeline steps
    steps = [
        ("build_combined_token.py", "Step 0a: Generate combined_token.csv files from trades"),
        ("build_date_group_token.py", "Step 0b: Generate date_group_token.csv files with value calculations"),
        ("analyze_all_users.py", "Step 1a: Analyze all users and calculate statistics"),
        ("segment_users.py", "Step 1b: Classify users into segments"),
        ("build_segment_positions_data.py", "Step 2: Build segment positions data"),
        ("build_segment_aggregation_data.py", "Step 3: Generate segment aggregations and comparison graphs"),
    ]
    
    # Check if all scripts exist
    print("\nChecking for required scripts...")
    missing_scripts = []
    for script_name, _ in steps:
        if not Path(script_name).exists():
            missing_scripts.append(script_name)
    
    if missing_scripts:
        print(f"✗ Missing scripts: {', '.join(missing_scripts)}")
        return 1
    
    print("✓ All scripts found")
    
    # Run each step
    total_start_time = time.time()
    total_steps = len(steps)
    
    for step_num, (script_name, description) in enumerate(steps, 1):
        success = run_script(script_name, description, step_num, total_steps)
        
        if not success:
            print(f"\n{'='*80}")
            print("Pipeline failed. Stopping execution.")
            print(f"{'='*80}\n")
            return 1
        
        # Show progress summary
        if step_num < total_steps:
            remaining_steps = total_steps - step_num
            elapsed = time.time() - total_start_time
            print(f"\nProgress: {step_num}/{total_steps} steps completed ({step_num*100//total_steps}%)")
            print(f"  {remaining_steps} step(s) remaining")
            print(f"  Total time so far: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)\n")
        
        # Small delay between steps for readability
        time.sleep(0.5)
    
    total_elapsed = time.time() - total_start_time
    
    print(f"\n{'='*80}")
    print("Pipeline completed successfully!")
    print(f"Total execution time: {total_elapsed:.2f} seconds")
    print(f"{'='*80}\n")
    
    # List generated outputs
    print("Generated outputs:")
    print("- combined_token_output/")
    print("- date_group_token_output/")
    print("- all_users_analysis.csv")
    print("- data_segment_output/")
    print("- data_segment/ (with CSV files and comparison graphs)")
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

