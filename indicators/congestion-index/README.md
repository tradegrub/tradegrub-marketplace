# Congestion Index

Measures how congested (consolidating) price action is by comparing the total N-bar range to the sum of individual bar ranges.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

- **N-bar range**: Highest high minus lowest low over the lookback window
- **Sum of bar ranges**: Sum of each bar's (high - low)
- **Congestion**: (1 - N_range / sum_ranges) * 100
- If price trends directionally, the N-bar range approaches the sum (low congestion)
- If price chops back and forth, the N-bar range is much smaller than the sum (high congestion)

## Parameters

- **Length** (default 14): Number of bars in the measurement window

## Signals

- **Above 70**: Tight consolidation, potential breakout building
- **Below 30**: Strong directional trend, low congestion
- **Rising congestion**: Trend losing momentum, transitioning to range
- **Background**: Purple tint when congestion exceeds 70

## Usage

Use to identify squeeze conditions before breakouts. High congestion followed by a sharp drop signals the start of a new trend. Pair with volume or momentum indicators to confirm breakout direction.
