# Time at Price Levels

![Concept](concept.svg)

Identifies price levels where the market has spent the most time consolidating. These dwell zones often act as strong support or resistance.

## How It Works

- Divides the recent price range into equal-sized bins
- Counts how many bars closed within each bin over the lookback period
- Plots the top 3 highest-count bins as horizontal lines on the price chart
- More time at a level = stronger potential support or resistance

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback | 200 | 50-500 | Number of bars to analyze |
| Number of Bins | 30 | 10-100 | Granularity of price level buckets |

## Outputs

- **Dwell Level 1**: Orange solid line at the most-visited price zone
- **Dwell Level 2**: Blue solid line at the second most-visited zone
- **Dwell Level 3**: Purple solid line at the third most-visited zone

## Usage Notes

- Price approaching a high-dwell level often stalls or reverses
- Breakouts through high-dwell levels tend to be significant
- Increase num_bins for finer-grained levels on lower timeframes
