# Cumulative Ratio Analysis - Implementation Summary

## What Was Created

A complete subfolder `cumulative_ratio_analysis/` with scripts and outputs for analyzing cumulative donation ratios on a **0-1 scale** (proportion-based).

## Key Improvements Over Previous Analysis

| Feature | Previous (Period-based) | New (Cumulative) |
|---------|------------------------|------------------|
| **Ratio Scale** | 0.5 to ∞ | 0 to 1 |
| **Numerator/Denominator** | (Dem + Rep) / Dem | Dem / (Dem + Rep) |
| **Interpretation** | Size ratio | Direct proportion |
| **Reference Point** | 2.0 (equal) | 0.5 (equal) |
| **Calculation** | Independent per period | Running total from start |

## Directory Structure

```
cumulative_ratio_analysis/
├── Scripts
│   ├── prepare_cumulative_donations.py    (Data preparation)
│   ├── plot_cumulative_donations.py       (Plot generation)
│   ├── run_cumulative_analysis.py         (Master orchestration)
│   └── README.md                          (Full documentation)
│
├── Data Outputs (output/)
│   ├── weekly_cumulative_aggregations.csv
│   ├── monthly_cumulative_aggregations.csv
│   └── cumulative_ratio_summary.csv
│
├── Plot Outputs - Normal Scale (plots_normal/)
│   ├── 8 Democratic ratio plots (Weekly + Monthly × All/Small/Medium/Large)
│   └── 8 Republican ratio plots (Weekly + Monthly × All/Small/Medium/Large)
│
└── Plot Outputs - Log Scale (plots_log/)
    ├── 8 Democratic ratio plots with log scaling
    └── 8 Republican ratio plots with log scaling
```

## Total Deliverables

- **32 Plots**: 16 normal scale + 16 log scale
- **3 CSV Files**: Aggregations + Summary statistics
- **4 Python Scripts**: Reusable, modular pipeline

## Quick Start

### Run Complete Analysis
```bash
cd cumulative_ratio_analysis
python3 run_cumulative_analysis.py
```

### Run Individual Steps
```bash
# Step 1: Prepare data (10-20 minutes)
python3 prepare_cumulative_donations.py

# Step 2: Generate plots (2-3 minutes)
python3 plot_cumulative_donations.py
```

## Key Findings

From the cumulative data:
- **Democratic Donations**: 72.65% of total ($371M)
- **Republican Donations**: 27.35% of total ($140M)
- **Total Records Processed**: 3.8M donations from 47,032 unique donors
- **Time Span**: January 2021 - September 2025
- **Donor Segments Analyzed**: All, Small, Medium, Large

## What Each Plot Shows

### Normal Scale (plots_normal/)
- Y-axis ranges 0 to 1
- Good for seeing overall proportion
- Horizontal line at 0.5 = equal donations
- **Visualization**: Ratio appears relatively flat when stuck at ~0.73

### Log Scale (plots_log/)
- Logarithmic y-axis scaling
- Better for seeing small variations
- Highlights deviation from equal donations
- **Visualization**: Variations near 0.5 become more visible and comparable

## Data Calculation Method

**Cumulative Ratio = Running Total / (Dem Running Total + Rep Running Total)**

Example for Democratic ratio:
```
Week 1: Dem = $100, Rep = $50
        Dem Ratio = 100 / (100+50) = 0.667

Week 2: Dem = $75, Rep = $100
        Cumulative Dem = $175, Cumulative Rep = $150
        Dem Ratio = 175 / (175+150) = 0.538

Week 3: Dem = $50, Rep = $50
        Cumulative Dem = $225, Cumulative Rep = $200
        Dem Ratio = 225 / (225+200) = 0.529
```

## Files Generated

### Scripts (4 files)
```
prepare_cumulative_donations.py    - Processes 70M records, creates aggregations
plot_cumulative_donations.py       - Generates 32 plots with normal + log scales
run_cumulative_analysis.py         - Master orchestration script
README.md                          - Full documentation with interpretation guide
```

### Data (3 files, ~100 KB total)
```
output/weekly_cumulative_aggregations.csv      - 782 rows
output/monthly_cumulative_aggregations.csv     - 228 rows
output/cumulative_ratio_summary.csv            - Summary statistics
```

### Plots (32 files, ~7 MB total)
```
plots_normal/     - 16 normal scale plots (~3.4 MB)
plots_log/        - 16 log scale plots (~3.5 MB)
```

## Visualization Details

Each plot includes:
- **Title**: Metric, Time Period, Donor Segment, Scale type
- **X-axis**: Time periods (weeks or months)
- **Y-axis**: Ratio value (0-1) with reference line at 0.5 (equal donations)
- **Line Chart**: Shows trend over time with markers
- **Color Coding**: 
  - Blue (#2E86AB) for Democratic metrics
  - Purple (#A23B72) for Republican metrics
- **Resolution**: 300 DPI (high quality)

## Sample Plots Available

Access plots from: `cumulative_ratio_analysis/plots_normal/` and `cumulative_ratio_analysis/plots_log/`

Examples:
- `cumulative_ratio_weekly_all_dem.png` - Democratic ratio by week (all donors)
- `cumulative_ratio_monthly_large_dem_log.png` - Democratic ratio by month, log scale (large donors)
- `cumulative_ratio_weekly_small_rep.png` - Republican ratio by week (small donors)

## Interpretation Guide

**Reading the plots:**

1. **Ratio = 0.5**: Both parties received equal cumulative donations
2. **Ratio > 0.5**: That party (Dem or Rep) received more cumulative donations
3. **Ratio < 0.5**: That party received fewer cumulative donations
4. **Flat line**: The ratio is stable over time
5. **Rising line**: That party's proportion of total donations is increasing
6. **Falling line**: That party's proportion of total donations is decreasing

**Normal vs Log scale:**
- **Normal scale**: Better for understanding overall proportions
- **Log scale**: Better for detecting small variations around 0.5

## Performance Statistics

- **Data processed**: 70.6M total donation records
- **Records kept**: 3.8M (from donors with segment classification)
- **Processing time**: ~10-15 minutes
- **Visualization time**: ~2-3 minutes
- **Total time**: ~15-20 minutes

## Technical Features

✓ Memory-efficient chunked processing (1M records per chunk)
✓ Vectorized pandas operations for performance
✓ Automatic date parsing (MMDDYYYY format)
✓ Cumulative sum calculations with proper handling of segments
✓ Ratio calculations with division-by-zero protection
✓ Professional matplotlib/seaborn visualizations
✓ High-resolution PNG exports (300 DPI)
✓ Comprehensive error handling and logging

## Next Steps

1. **Review plots**: Start with normal scale plots in `plots_normal/`
2. **Analyze trends**: Look for inflection points or changes in ratio
3. **Compare segments**: See how Small/Medium/Large donors differ
4. **Check log scale**: Use log-scale versions to spot small variations
5. **Aggregate insights**: Review `cumulative_ratio_summary.csv` for statistics

## Documentation

Full detailed documentation is in: [cumulative_ratio_analysis/README.md](cumulative_ratio_analysis/README.md)

Includes:
- Detailed methodology
- Complete plot listings with links
- Interpretation guidelines
- Troubleshooting section
- Technical specifications
