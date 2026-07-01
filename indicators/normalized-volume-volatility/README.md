## Normalized Volume Volatility

Normalizes volume and ATR-based volatility against their historical statistical baselines. The baseline is calculated as the rolling mean plus a configurable number of standard deviations over a lookback window. Output is scaled so that 100 represents the baseline level: readings above 100 indicate above-normal activity, readings below 100 indicate below-normal activity.

Includes a linear regression trend line fitted to the normalized volume values to reveal the longer-term direction of volume participation.

### How it works

1. For each bar, compute rolling mean and standard deviation of volume over the lookback period
2. Baseline = mean + (sigma threshold x standard deviation)
3. Normalized value = (current value / baseline) x 100
4. The same normalization is applied to ATR for volatility
5. A linear regression line is fitted across all normalized volume readings

### Parameters

- **Lookback Period**: Rolling window for mean and standard deviation calculation (default: 50)
- **Sigma Threshold**: Number of standard deviations added to the mean for the baseline (default: 1.0)
- **Show Volatility**: Toggle the normalized ATR volatility line (default: on)
- **Show Regression**: Toggle the linear regression trend line (default: on)

### Reading the indicator

- **Green bars above 100**: Volume exceeds the statistical baseline
- **Red bars below 100**: Volume is below the statistical baseline
- **Orange line**: Normalized volatility (ATR), same 100 baseline interpretation
- **Blue dashed line**: Linear regression trend of normalized volume
- **White dashed line at 100**: The normal activity threshold


## Conceptual Diagram

![Concept](concept.svg)
