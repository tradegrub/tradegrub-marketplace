# Topographic Volume Nodes

Uses a terrain prominence algorithm to identify the most significant high-volume price levels.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

1. Builds a volume profile by distributing each bar's volume across price bins
2. Detects local maxima (peaks) in the volume distribution
3. Computes the "prominence" of each peak, measuring how much it stands above surrounding valleys
4. Displays the top 3 most prominent levels as horizontal lines

## Parameters

- **Lookback Period** (default 200): Number of bars to analyze for building the volume profile
- **Number of Bins** (default 50): Resolution of the price histogram

## Signals

- High-prominence volume nodes act as strong support/resistance
- Price tends to consolidate around these levels
- Breakouts from high-volume nodes often lead to sustained moves

## Usage

Add as an overlay to identify key volume-based support and resistance levels. The three displayed levels represent the price zones where the most significant volume clustering occurred over the lookback period. Higher prominence means the level is more dominant relative to surrounding price action.
