# Statistical Bin S/R

Identifies support and resistance levels by binning recent closing prices into a histogram and finding the most populated price zones.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

1. Divides the recent price range into N equal-width bins using numpy
2. Counts how many closes fall into each bin
3. The top 3 bins by count represent the strongest S/R zones
4. Plots the midpoint of each top bin as a horizontal line on the chart

## Parameters

- **Lookback** (default 100): Number of bars to analyze
- **Num Bins** (default 20): Number of price bins to divide the range into

## Signals

- **Green line**: Lowest S/R level (likely support)
- **Orange line**: Middle S/R level
- **Red line**: Highest S/R level (likely resistance)

## Usage

Use as objective, data-driven support and resistance. More closes in a bin means price has spent significant time there, creating a natural magnet. Combine with volume profile for stronger confluence. Increase bins for finer resolution or decrease for broader zones.
