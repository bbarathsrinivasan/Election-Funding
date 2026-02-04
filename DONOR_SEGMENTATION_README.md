# Donor Segmentation Analysis

## Overview

This analysis segments election donors into three distinct groups based on their cumulative donation amounts. The segmentation allows us to understand donation patterns and behaviors across different donor types.

## Methodology

### Segmentation Approach

Donors are classified into three segments using **percentile-based thresholds**:

1. **Small Donors** (Bottom 33.3%)
   - Cumulative donations ≤ 33.3rd percentile
   - Typically grass-roots, individual contributors
   - Represent a large number of donors but smaller donation amounts per person

2. **Medium Donors** (33.3rd - 66.6th percentile)
   - Cumulative donations between 33.3rd and 66.6th percentile
   - Committed contributors with moderate funding power
   - Balance between donation count and amount per donor

3. **Large Donors** (Top 33.3%)
   - Cumulative donations > 66.6th percentile
   - Major contributors with significant financial capacity
   - Smaller in number but larger donation amounts per person

### Why Percentile-Based Thresholds?

- **Adaptive to data**: Thresholds automatically adjust based on actual donation distribution
- **Equal segmentation**: Attempts to create three roughly equal-sized groups (by percentile)
- **Interpretable**: Easy to understand and communicate (top 33%, middle 33%, bottom 33%)
- **Robust**: Less sensitive to outliers compared to fixed dollar amounts

## Data Files

### Input Files
- `Filtered_US_Election_Donation.csv` - Election donation records (filtered for target candidates)
- `US_Election_Donation.csv` - Full election donation data (fallback)

### Output Files
- `donor_segments.csv` - Donor segmentation results with statistics
- `donor_segmentation_diagrams/` - Folder containing all visualizations and statistics
  - `donor_segments_visualization.png` - 6-panel comprehensive dashboard
  - `donor_cumulative_distribution.png` - Cumulative distribution analysis
  - `donor_segment_statistics.csv` - Detailed statistics table

## Visualizations

All visualizations are saved in the `donor_segmentation_diagrams/` folder.

### Main Dashboard: Six-Panel Visualization

![Donor Segments Visualization](donor_segmentation_diagrams/donor_segments_visualization.png)

This comprehensive dashboard includes:

**1. Number of Donors by Segment (Top-Left: Bar Chart)**
Shows the count of donors in each segment.
- Typically shows more donors in Small and Medium segments
- Large segment is the smallest numerically

**2. Percentage of Donors by Segment (Top-Middle: Pie Chart)**
Displays the percentage distribution of donor counts across segments.

**3. Total Amount Donated by Segment (Top-Right: Bar Chart)**
Shows the total dollar amount donated by each segment.
- Often reveals that Large donors contribute disproportionately to total funding
- Demonstrates concentration of donations in the Large segment

**4. Distribution of Donation Amounts (Bottom-Left: Box Plot)**
Illustrates the range and variability of individual donation amounts within each segment.
- Shows median, quartiles, and outliers
- Reveals spread of donation sizes within each segment

**5. Average Donation per Donor (Bottom-Middle: Bar Chart)**
Average donation amount for donors in each segment.
- Increases from Small to Large segment
- Shows the typical donor's contribution level in each segment

**6. Average Number of Donations per Donor (Bottom-Right: Bar Chart)**
Average frequency of donations per donor in each segment.
- Indicates engagement level and commitment
- Helps understand if segment is defined by frequency or amount

### Cumulative Distribution Plot

![Cumulative Distribution](donor_segmentation_diagrams/donor_cumulative_distribution.png)

Shows cumulative percentage of donations as you move through donors in each segment.
- Helps identify concentration patterns within segments
- Reveals if a few donors dominate within a segment
- Each line represents one segment showing how donations accumulate

## Statistical Summary

The analysis provides the following statistics for each segment:
- **Count**: Number of donors
- **Percentage**: % of total donors
- **Total Donated**: Total $ donated by segment
- **% of Total**: % of total donations
- **Average**: Mean donation amount per donor
- **Median**: Median donation amount
- **Min/Max**: Range of donation amounts
- **Avg # Donations**: Average frequency of donations

## Key Insights

Typical patterns revealed by donor segmentation:

1. **Large donors often drive funding**: Despite being fewer in number, Large donors typically contribute a significant portion of total funds.

2. **Small donors provide volume**: Small donors make up the majority of donor base but contribute lower amounts individually.

3. **Medium donors bridge the gap**: Medium donors represent a middle ground in both participation and contribution levels.

4. **Engagement patterns vary**: Different segments may show different donation frequencies, revealing engagement levels.

5. **Donation concentration**: Analysis reveals how concentrated or distributed donations are within and across segments.

## Scripts

### Main Scripts
- `segment_election_donors.py` - Core segmentation script
- `visualize_donor_segments.py` - Creates visualizations and statistics

### Pipeline Integration
These scripts are part of the larger Election Funding analysis pipeline:
1. `filter_candidates.py` - Filter to target candidates
2. `segment_election_donors.py` - Segment donors (you are here)
3. `visualize_donor_segments.py` - Visualize segments
4. `segment_users.py` - Segment prediction market participants
5. `build_*.py` - Build token and position data
6. `build_segment_*.py` - Build segment-specific analysis

## Running the Analysis

### Step 1: Segment Donors
```bash
python segment_election_donors.py
```
This creates `donor_segments.csv` with donor classifications.

### Step 2: Visualize Segments
```bash
python visualize_donor_segments.py
```
This generates visualizations and statistics tables.

### Step 3: Run All (using orchestrator)
```bash
python orchestration_script.py
```
Runs the complete pipeline in order.

## Interpretation Guide

### When to use this segmentation:
- Understanding funding source diversity
- Identifying influential donor groups
- Analyzing donation patterns by contributor type
- Comparing how different segments behave in prediction markets
- Policy analysis on campaign finance concentration

### Limitations:
- Snapshot analysis (doesn't account for donation timing)
- Doesn't consider candidate preferences
- Percentile thresholds may vary across election cycles
- Single metric (total amount) doesn't capture motivation or impact

## Future Extensions

Potential enhancements to donor segmentation:
- Time-series analysis of donation timing
- Candidate preference analysis by segment
- Geographic segmentation
- Demographic analysis (if available)
- Donation timing patterns (early vs. late donors)
- Repeat donor analysis (loyalty metrics)
- Correlation with prediction market activity

## Technical Details

### Required Libraries
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `matplotlib` - Plotting
- `seaborn` - Statistical visualization

### Data Processing
- Converts donation amounts to numeric values
- Handles missing or zero values
- Removes donors with zero cumulative donations
- Sorts output by donation amount (descending)

### Performance
- Efficiently handles large datasets using pandas groupby operations
- Generates high-resolution visualizations (300 DPI)
- Produces reproducible results (deterministic percentile calculations)

## Questions & Contact

For questions about this analysis or to request modifications, refer to the main project documentation or contact the research team.
