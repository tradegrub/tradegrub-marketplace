# Candle Density Indicator

Measures how many candle bodies overlap at each price level to identify congestion zones.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

1. Divides the recent price range into bins
2. For each bin, counts how many candle bodies (open-to-close range) overlap that price level
3. Normalizes the count to a 0-100 scale
4. Each bar's score is the average density of the bins its body covers

## Parameters

- **Lookback Period** (default 50): Number of bars to analyze
- **Number of Bins** (default 30): Resolution of the price histogram

## Signals

- High density (above 75): Price is in a congestion zone with heavy overlap, expect choppy action
- Low density (below 25): Price is in a clean zone with little prior overlap, expect trending behavior
- Transitions from high to low density can signal breakout opportunities

## Usage

Use to identify whether the current price is in a congested or clear zone. Congestion zones often lead to range-bound trading, while low-density areas allow for directional moves. Combine with volume indicators for stronger signals.
