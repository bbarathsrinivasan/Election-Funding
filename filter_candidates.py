#!/usr/bin/env python3
"""
Script to filter US_Election_Donation.csv to keep only rows for 
LAKE, KARI and GALLEGO, RUBEN candidates.
"""

import pandas as pd
import os

# File paths
input_file = "US_Election_Donation.csv"
output_file = "Filtered_US_Election_Donation.csv"

# Target candidates
target_candidates = ["LAKE, KARI", "GALLEGO, RUBEN"]

print(f"Reading {input_file}...")

# Read the CSV file
# Using chunksize for large files to be memory efficient
chunk_size = 100000
chunks = []
total_rows = 0
filtered_rows = 0

try:
    for chunk in pd.read_csv(input_file, chunksize=chunk_size, low_memory=False):
        total_rows += len(chunk)
        # Filter rows where Candidate is in target_candidates
        filtered_chunk = chunk[chunk['Candidate'].isin(target_candidates)]
        filtered_rows += len(filtered_chunk)
        
        if len(filtered_chunk) > 0:
            chunks.append(filtered_chunk)
        
        print(f"Processed {total_rows:,} rows, found {filtered_rows:,} matching rows...")
    
    if chunks:
        # Combine all filtered chunks
        print("Combining filtered data...")
        filtered_df = pd.concat(chunks, ignore_index=True)
        
        # Write back to the same file
        print(f"Writing filtered data to {output_file}...")
        filtered_df.to_csv(output_file, index=False)
        
        print(f"\nFiltering complete!")
        print(f"Original rows: {total_rows:,}")
        print(f"Filtered rows: {filtered_rows:,}")
        print(f"Rows removed: {total_rows - filtered_rows:,}")
        print(f"\nKept candidates: {', '.join(target_candidates)}")
    else:
        print("No rows found matching the target candidates.")
        
except Exception as e:
    print(f"Error: {e}")
    raise


