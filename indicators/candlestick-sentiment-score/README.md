# Candlestick Sentiment Score

Quantifies bar-by-bar sentiment by analyzing three components of each candlestick: body direction (bullish/bearish), close position within the range (high=bullish, low=bearish), and wick bias (longer lower wicks=bullish). The weighted composite is averaged and smoothed into a single oscillator.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Scoring Lookback** (3-50, default 10): Rolling window for averaging raw bar scores
- **Smoothing Length** (1-20, default 5): Additional smoothing on the averaged score
- **Color Score Bars** (default on): Display as colored histogram instead of line

## Signals

- **Positive values**: Bullish sentiment (green bars)
- **Negative values**: Bearish sentiment (red bars)
- **Above +30**: Strong bullish conviction
- **Below -30**: Strong bearish conviction
- **Zero crossovers**: Sentiment shift points

## Use Cases

- Gauge short-term directional bias from price action alone
- Confirm trend strength when aligned with trend indicators
- Spot sentiment divergences when score weakens while price continues
