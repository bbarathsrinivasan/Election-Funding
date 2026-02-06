# Cumulative Ratio Analysis vs Period-Based Analysis

## Side-by-Side Comparison

### Scale & Ratios

| Aspect | Period-Based | Cumulative |
|--------|--------------|-----------|
| **Ratio Formula (Dem)** | (Dem + Rep) / Dem | Dem / (Dem + Rep) |
| **Ratio Formula (Rep)** | (Dem + Rep) / Rep | Rep / (Dem + Rep) |
| **Minimum Value** | 1.0 | 0.0 |
| **Maximum Value** | ∞ | 1.0 |
| **Equal Donations** | 2.0 | 0.5 |
| **Example (Dem gets $100, Rep gets $50)** | (150)/100 = 1.5 | 100/(150) = 0.667 |
| **Interpretability** | Size ratio | Direct proportion |

### Calculation Method

| Aspect | Period-Based | Cumulative |
|--------|--------------|-----------|
| **Jan**: Dem = $100, Rep = $50 | Ratio = 1.5 | Ratio = 0.667 |
| **Feb**: Dem = $75, Rep = $100 | Ratio = 1.75 | **Cumulative** Dem = $175, Rep = $150<br/>Ratio = 0.538 |
| **Mar**: Dem = $50, Rep = $50 | Ratio = 2.0 | **Cumulative** Dem = $225, Rep = $200<br/>Ratio = 0.529 |
| **Visualization** | Each month independent | Shows trend over time |

### Visualization Approach

| Aspect | Period-Based | Cumulative |
|--------|--------------|-----------|
| **Output Folders** | `donation_time_series_plots/` | `cumulative_ratio_analysis/` |
| **Plot Types** | Ratio plots + Donation amounts | Ratio plots only |
| **Scales Available** | Normal + Log | Normal + Log |
| **Total Plots** | 64 plots (32 ratio + 32 donation) | 32 plots (ratio only) |
| **Normal Scale** | 0.5 to ∞ range | 0 to 1 range |
| **Log Scale** | For extreme ratios | For subtle variations |

### When to Use Each

**Use Period-Based Analysis When:**
- ✓ You want to see donation amounts alongside ratios
- ✓ You need 64 comprehensive visualizations
- ✓ You're interested in actual dollar amounts
- ✓ You want both ratio and absolute data
- ✓ Analyzing donation trends independently

**Use Cumulative Analysis When:**
- ✓ You want direct proportion/percentage of donations
- ✓ You care about the running trend from start
- ✓ 0-1 scale is more intuitive for your audience
- ✓ You want 32 focused ratio plots only
- ✓ You need easy interpretation (0.5 = equal)

---

## Detailed Formula Comparison

### Example Scenario
Over 3 months, donations are:
```
January:   Democratic: $100,000   Republican: $50,000
February:  Democratic: $75,000    Republican: $100,000
March:     Democratic: $50,000    Republican: $50,000
```

### Period-Based Calculation

**January Ratio**
```
Democratic: (100,000 + 50,000) / 100,000 = 150,000 / 100,000 = 1.5
Republican: (100,000 + 50,000) / 50,000 = 150,000 / 50,000 = 3.0
```

**February Ratio**
```
Democratic: (75,000 + 100,000) / 75,000 = 175,000 / 75,000 = 2.33
Republican: (75,000 + 100,000) / 100,000 = 175,000 / 100,000 = 1.75
```

**March Ratio**
```
Democratic: (50,000 + 50,000) / 50,000 = 100,000 / 50,000 = 2.0
Republican: (50,000 + 50,000) / 50,000 = 100,000 / 50,000 = 2.0
```

### Cumulative Calculation

**January Ratio**
```
Cumulative Dem: 100,000
Cumulative Rep: 50,000
Democratic: 100,000 / (100,000 + 50,000) = 100,000 / 150,000 = 0.667
Republican: 50,000 / 150,000 = 0.333
```

**February Ratio**
```
Cumulative Dem: 100,000 + 75,000 = 175,000
Cumulative Rep: 50,000 + 100,000 = 150,000
Democratic: 175,000 / (175,000 + 150,000) = 175,000 / 325,000 = 0.538
Republican: 150,000 / 325,000 = 0.462
```

**March Ratio**
```
Cumulative Dem: 175,000 + 50,000 = 225,000
Cumulative Rep: 150,000 + 50,000 = 200,000
Democratic: 225,000 / (225,000 + 200,000) = 225,000 / 425,000 = 0.529
Republican: 200,000 / 425,000 = 0.471
```

---

## Visual Differences

### Period-Based Chart (Y-axis: 0.5 to ∞)
```
Ratio
  |     Dem: 2.33
  |       *
  |     / 
  |   *  (Dem: 1.5)
  |
  +---+---+---
    Jan Feb Mar
    
The ratios vary widely (1.5, 2.33, 2.0)
Difficult to see subtle differences
```

### Cumulative Chart (Y-axis: 0 to 1)
```
Ratio
  1 |
    |
  0.7|   * (0.667)
    |   |
  0.5|---|---- (Equal line)
    |   |  
    |   |  * (0.538)
    |   |   \
  0.3|       * (0.529)
    |
  0 +---+---+---
    Jan Feb Mar

The ratios move smoothly from 0.667 → 0.538 → 0.529
Easy to see the declining trend
Proportions are immediately clear
```

### Log Scale Cumulative (Better detail near 0.5)
```
Ratio (log scale)
  1.0 |
      |
  0.7 |   * (0.667)
      |   |
  0.5 |---|---- (Equal line - expands here)
      |   |
      |   | * (0.538)
  0.3 |    \
      |     * (0.529)
      |
  0.0 +---+---+---
    Jan Feb Mar

Variations magnified around 0.5
Better visibility of subtle changes
```

---

## Real Data Example

### From Our Analysis

**Democratic Donations Over Time**

Period-Based View (Period-only):
```
Jan 2021: Dem ratio = 1.0 (only Dem donations in period)
Feb 2021: Dem ratio = infinite (only Dem donations)
Apr 2021: Dem ratio = 0.215 (mostly Rep donations in that month)
May 2021: Dem ratio = 0.244 (mostly Rep donations in that month)
```

Cumulative View (Running total):
```
Jan 2021: Dem ratio = 1.0 (only Dem so far)
Feb 2021: Dem ratio = 1.0 (still only Dem)
Apr 2021: Dem ratio = 0.215 (Dem finally received some Rep donations)
May 2021: Dem ratio = 0.244 (Cumulative Dem < Dem+Rep)
...
Final (Sep 2025): Dem ratio = 0.7265 (Overall: 72.65% to Dem)
```

---

## File Organization

```
Root Directory
├── donation_time_series_plots/            (Period-based: 64 plots)
│   ├── cumulative_ratio_*.png             (16 ratio plots)
│   ├── dem_donations_*.png                (16 Dem donation plots)
│   ├── rep_donations_*.png                (16 Rep donation plots)
│   └── donation_time_series_plots_log/    (16 log-scale ratio plots)
│
└── cumulative_ratio_analysis/             (Cumulative: 32 plots)
    ├── plots_normal/                      (16 normal scale)
    │   ├── cumulative_ratio_*_dem.png
    │   └── cumulative_ratio_*_rep.png
    ├── plots_log/                         (16 log scale)
    │   ├── cumulative_ratio_*_dem_log.png
    │   └── cumulative_ratio_*_rep_log.png
    ├── output/                            (Data CSVs)
    └── README.md                          (Full documentation)
```

---

## Summary Decision Matrix

| Need | Use |
|------|-----|
| Direct proportions (%) | **Cumulative** |
| 0-1 scale intuitive | **Cumulative** |
| Running trend from start | **Cumulative** |
| Actual donation amounts | **Period-Based** |
| Complete analysis (both views) | **Both** |
| Focused on ratios only | **Cumulative** |
| Size ratios (vs other party) | **Period-Based** |
| Audience unfamiliar with ratios | **Cumulative** |
| Academic/research publication | **Both** (explain differences) |

---

## Integration Notes

Both analyses can coexist:
- **Period-Based** in `donation_time_series_plots/` - Keep for reference
- **Cumulative** in `cumulative_ratio_analysis/` - Use for proportion analysis

They answer different questions:
1. **Period-Based**: "How do donations in each period compare?"
2. **Cumulative**: "What's our overall proportion trend?"

Use both for comprehensive insights into election donation dynamics.
