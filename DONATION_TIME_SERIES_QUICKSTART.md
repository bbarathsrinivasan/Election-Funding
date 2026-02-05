# Donation Time Series Analysis - Quick Start Guide

## What This Does

Generates **32 plots** showing:
- Democratic and Republican donation trends over time
- Segmented by donor size (All, Small, Medium, Large)
- Weekly and monthly views
- Cumulative ratio analysis for both parties

## Quick Run

```bash
# Run everything (takes ~15-25 minutes)
python3 run_donation_time_series_analysis.py
```

## What You'll Get

### 1. Cumulative Ratio Plots (16 total)

**Democratic Ratio = (Dem + Rep) / Dem**
- 8 plots (weekly/monthly × all/small/medium/large)
- Shows if Dem donations are above/below parity

**Republican Ratio = (Dem + Rep) / Rep**
- 8 plots (weekly/monthly × all/small/medium/large)
- Shows if Rep donations are above/below parity

### 2. Party Donation Plots (16 total)

**Democratic Donations Over Time**
- 8 plots (weekly/monthly × all/small/medium/large)
- Bar charts showing actual donation amounts

**Republican Donations Over Time**
- 8 plots (weekly/monthly × all/small/medium/large)
- Bar charts showing actual donation amounts

## Output Structure

```
donation_time_series_plots/
├── cumulative_ratio_weekly_all_dem.png       # Dem ratio - all donors, weekly
├── cumulative_ratio_weekly_small_dem.png     # Dem ratio - small donors, weekly
├── cumulative_ratio_weekly_medium_dem.png    # Dem ratio - medium donors, weekly
├── cumulative_ratio_weekly_large_dem.png     # Dem ratio - large donors, weekly
├── cumulative_ratio_monthly_all_dem.png      # Dem ratio - all donors, monthly
├── cumulative_ratio_monthly_small_dem.png    # Dem ratio - small donors, monthly
├── cumulative_ratio_monthly_medium_dem.png   # Dem ratio - medium donors, monthly
├── cumulative_ratio_monthly_large_dem.png    # Dem ratio - large donors, monthly
├── cumulative_ratio_weekly_all_rep.png       # Rep ratio - all donors, weekly
├── cumulative_ratio_weekly_small_rep.png     # Rep ratio - small donors, weekly
├── cumulative_ratio_weekly_medium_rep.png    # Rep ratio - medium donors, weekly
├── cumulative_ratio_weekly_large_rep.png     # Rep ratio - large donors, weekly
├── cumulative_ratio_monthly_all_rep.png      # Rep ratio - all donors, monthly
├── cumulative_ratio_monthly_small_rep.png    # Rep ratio - small donors, monthly
├── cumulative_ratio_monthly_medium_rep.png   # Rep ratio - medium donors, monthly
├── cumulative_ratio_monthly_large_rep.png    # Rep ratio - large donors, monthly
├── dem_donations_weekly_all.png              # Dem donations - all donors, weekly
├── dem_donations_weekly_small.png            # Dem donations - small donors, weekly
├── dem_donations_weekly_medium.png           # Dem donations - medium donors, weekly
├── dem_donations_weekly_large.png            # Dem donations - large donors, weekly
├── dem_donations_monthly_all.png             # Dem donations - all donors, monthly
├── dem_donations_monthly_small.png           # Dem donations - small donors, monthly
├── dem_donations_monthly_medium.png          # Dem donations - medium donors, monthly
├── dem_donations_monthly_large.png           # Dem donations - large donors, monthly
├── rep_donations_weekly_all.png              # Rep donations - all donors, weekly
├── rep_donations_weekly_small.png            # Rep donations - small donors, weekly
├── rep_donations_weekly_medium.png           # Rep donations - medium donors, weekly
├── rep_donations_weekly_large.png            # Rep donations - large donors, weekly
├── rep_donations_monthly_all.png             # Rep donations - all donors, monthly
├── rep_donations_monthly_small.png           # Rep donations - small donors, monthly
├── rep_donations_monthly_medium.png          # Rep donations - medium donors, monthly
├── rep_donations_monthly_large.png           # Rep donations - large donors, monthly
└── donation_time_series_summary.csv          # Summary statistics
```

## Interpreting the Ratios

### Democratic Ratio: (Dem + Rep) / Dem

| Ratio Value | Meaning |
|-------------|---------|
| 2.0 | Equal donations from both parties |
| > 2.0 | More Democratic donations (e.g., 3.0 = Dem has 67%) |
| < 2.0 | Fewer Democratic donations (e.g., 1.5 = Dem has 33%) |

### Republican Ratio: (Dem + Rep) / Rep

| Ratio Value | Meaning |
|-------------|---------|
| 2.0 | Equal donations from both parties |
| > 2.0 | More Republican donations (e.g., 3.0 = Rep has 67%) |
| < 2.0 | Fewer Republican donations (e.g., 1.5 = Rep has 33%) |

## Prerequisites

1. **donor_segments.csv** must exist
   - Run `segment_election_donors.py` if missing

2. **US_Election_Donation.csv** must exist
   - ~70M donation records

## Troubleshooting

**"donor_segments.csv not found"**
→ Run: `python3 segment_election_donors.py`

**"Out of memory"**
→ Edit `prepare_donation_time_series.py`, reduce `chunk_size` on line 54

**Process is slow**
→ Normal! Processing 70M records takes time. Grab coffee ☕

## File Sizes (Approximate)

- processed_donations.csv: ~500MB-1GB
- weekly_aggregations.csv: ~500KB
- monthly_aggregations.csv: ~100KB
- Each plot: ~200-500KB

## Need Help?

See full documentation: [DONATION_TIME_SERIES_README.md](DONATION_TIME_SERIES_README.md)
