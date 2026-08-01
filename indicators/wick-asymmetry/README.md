# Wick Asymmetry Ratio

A bounded oscillator (-1 to +1) measuring the asymmetry between upper and lower candle wicks.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

For each bar, the indicator computes:

- Upper wick: high minus the greater of open/close
- Lower wick: the lesser of open/close minus low
- WAR: (lower_wick - upper_wick) / (upper_wick + lower_wick + epsilon)

The raw ratio is smoothed with an EMA to reduce noise.

## Parameters

- **Smoothing Length** (default 10): EMA period for smoothing the raw ratio

## Signals

- Positive values: more lower wicks, indicating buying pressure (buyers stepping in at lows)
- Negative values: more upper wicks, indicating selling pressure (sellers rejecting highs)
- Readings above 0.5 or below -0.5 are highlighted as extreme
- Zero crossovers can signal shifts in pressure

## Usage

Use as a confirmation tool for trend direction or reversal detection. Persistent positive readings during an uptrend confirm healthy buying. Divergence between price direction and wick asymmetry can signal weakening momentum.
