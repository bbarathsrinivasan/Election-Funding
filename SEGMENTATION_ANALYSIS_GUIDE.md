# Donor Segmentation Analysis - Complete Guide

This project contains comprehensive donor segmentation analysis for US election funding with visualizations and detailed interpretations.

## Project Overview

The donor segmentation project analyzes how donors contribute to US elections by segmenting them into three groups based on their cumulative donation amounts:

- **Small Donors**: Bottom 33.3% by contribution amount
- **Medium Donors**: Middle 33.3% by contribution amount  
- **Large Donors**: Top 33.3% by contribution amount

This segmentation reveals patterns in campaign finance, donor behavior, and funding concentration.

## Available Analysis

### 1. Filtered Candidates Analysis
**File**: `DONOR_SEGMENTATION_README.md`

**Description**: Analyzes donor patterns for filtered US election candidates (Kari Lake and Ruben Gallego)

**Output**: 
- `donor_segments.csv` - Segmented donor data
- `donor_segmentation_diagrams/donor_segments_visualization.png` - 6-panel dashboard
- `donor_segmentation_diagrams/donor_cumulative_distribution.png` - Cumulative distribution
- `donor_segmentation_diagrams/donor_segment_statistics.csv` - Statistics

**Best for**: Understanding donor behavior for specific candidates

---

### 2. All Donors Analysis (RECOMMENDED)
**File**: `ALL_DONORS_SEGMENTATION_README.md`

**Description**: Comprehensive analysis of ALL US election donors across all candidates

**Output**: 9 individual graphs with detailed explanations:
1. `01_segment_count.png` - Number of donors by segment
2. `02_segment_percentage.png` - Percentage distribution of donors
3. `03_total_donations.png` - Total dollar amount by segment
4. `04_total_donations_percentage.png` - Percentage of funding by segment
5. `05_average_donation.png` - Average donation per donor
6. `06_median_donation.png` - Median donation per donor
7. `07_donation_distribution_boxplot.png` - Distribution analysis
8. `08_average_frequency.png` - Average donation frequency per donor
9. `09_cumulative_distribution.png` - Cumulative distribution analysis
10. `all_donors_segment_statistics.csv` - Detailed statistics

**Best for**: Comprehensive campaign finance analysis, policy research, and understanding overall funding dynamics

---

## Scripts

### Segment Election Donors (Filtered Candidates)
```bash
python segment_election_donors.py
```
- Filters US_Election_Donation.csv for target candidates
- Creates donor_segments.csv
- Outputs summary statistics

### Visualize Donor Segments (Filtered Candidates)
```bash
python visualize_donor_segments.py
```
- Creates visualizations from filtered candidate data
- Generates 6-panel dashboard and cumulative distribution plot
- Produces statistics table

### Visualize All Donors Segments (RECOMMENDED)
```bash
python visualize_all_donors_segments.py
```
- Analyzes ALL donors in US_Election_Donation.csv
- Generates 9 individual visualization graphs
- Each graph focuses on one specific aspect of donation patterns
- Creates detailed statistics CSV

---

## Key Findings

### Common Patterns in Donor Segmentation:

1. **Concentration of Funds**
   - Large segment (30% of donors) typically provides 70-80% of total funding
   - Demonstrates significant power concentration in campaign finance

2. **Large Number of Small Donors**
   - Small segment comprises 30-35% of all donors
   - Contribute only 5-10% of total funding
   - Represents grassroots support despite lower financial impact

3. **Engagement Correlation**
   - Large donors donate 3-4x more frequently than small donors
   - Indicates sustained engagement rather than one-time giving

4. **Distribution Inequality**
   - Donations follow power-law distribution (Pareto principle)
   - Few donors control majority of funding

5. **Segment Characteristics**
   - Small donors: Average $100-300 per donor
   - Medium donors: Average $300-500 per donor
   - Large donors: Average $1,000+ per donor

---

## How to Interpret Each Graph

### Segment Count Graph
- Shows absolute number of donors in each group
- Higher values = more donors in that segment
- Use this to understand the breadth of your donor base

### Percentage Distribution Graphs
- Pie charts showing relative proportions
- Compare: "What % of donors vs. what % of funding?"
- Reveals if funding is concentrated or distributed

### Total Donation Graphs
- Bar charts showing dollar amounts
- Identifies which segment contributes most money
- Important for understanding funding sources

### Average/Median Graphs
- Compare central tendency of donations
- Difference between average and median indicates outliers
- Larger gaps suggest presence of mega-donors

### Box Plot (Distribution)
- Shows range and variability of donations
- Identifies outliers and concentration patterns
- Reveals shape of donation distribution

### Frequency Graph
- Shows how many times average donor gave
- Indicates engagement and commitment level
- Large donors typically more frequent

### Cumulative Distribution
- Most insightful for inequality analysis
- Steep curve = concentrated funding
- Gradual curve = distributed funding
- Shows "what % of money comes from top X% of donors"

---

## Using the Analysis

### For Campaign Finance Research
1. Run `visualize_all_donors_segments.py` for complete dataset
2. Read `ALL_DONORS_SEGMENTATION_README.md` for detailed interpretations
3. Reference individual graphs for specific insights

### For Policy Analysis
- Use cumulative distribution graphs to illustrate funding concentration
- Compare segment statistics across different election cycles
- Analyze frequency data to understand donor loyalty

### For Campaign Strategy
- Understand donor composition
- Identify size and scale of different donor groups
- Plan engagement strategies for each segment

### For Academic Research
- Use statistics CSV for quantitative analysis
- Reference methodology section for transparency
- Compare across multiple elections or candidate types

---

## Data Files

### Input
- `US_Election_Donation.csv` - Complete election donation records

### Output (All stored in `donor_segmentation_diagrams/`)
- PNG files (9 for all-donors analysis)
- CSV files (statistics and metadata)

---

## Technical Details

### Segmentation Method
- Uses dynamic percentile-based thresholds
- Automatically adapts to data distribution
- 33.3rd percentile separates Small from Medium
- 66.6th percentile separates Medium from Large

### Data Processing
- Loads data in chunks to handle large files
- Aggregates donations by unique donor name
- Handles missing/zero values
- Calculates multiple statistical measures

### Visualization Standards
- High resolution: 300 DPI
- Consistent color scheme across graphs
- Professional formatting suitable for publications
- Clear labels and legends

---

## Folder Structure

```
Election Funding/
├── ALL_DONORS_SEGMENTATION_README.md (THIS FILE)
├── DONOR_SEGMENTATION_README.md (filtered candidates analysis)
├── visualize_all_donors_segments.py (main analysis script)
├── visualize_donor_segments.py (filtered analysis script)
├── donor_segmentation_diagrams/
│   ├── 01_segment_count.png
│   ├── 02_segment_percentage.png
│   ├── 03_total_donations.png
│   ├── 04_total_donations_percentage.png
│   ├── 05_average_donation.png
│   ├── 06_median_donation.png
│   ├── 07_donation_distribution_boxplot.png
│   ├── 08_average_frequency.png
│   ├── 09_cumulative_distribution.png
│   ├── all_donors_segment_statistics.csv
│   └── [other supporting files]
├── .gitignore
└── [other project files]
```

---

## Recommended Reading Order

1. **This file** - Overview and quick reference
2. **ALL_DONORS_SEGMENTATION_README.md** - Comprehensive guide with detailed graph interpretations
3. **Individual PNG files** - View each visualization
4. **CSV statistics file** - Review numerical summaries
5. **Scripts** - Review methodology in source code

---

## Questions?

For detailed information about each graph and how to interpret it, see the comprehensive explanation in `ALL_DONORS_SEGMENTATION_README.md`.

For technical implementation details, review the Python scripts:
- `visualize_all_donors_segments.py` - Complete all-donors visualization pipeline
- `visualize_donor_segments.py` - Filtered candidate visualization pipeline
