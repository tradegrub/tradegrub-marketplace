# Double Bollinger Bands

Plots two sets of Bollinger Bands with different standard deviation multipliers around the same simple moving average. The default configuration uses 1 standard deviation for the inner bands and 2 standard deviations for the outer bands.

## Conceptual Diagram

![Concept](concept.svg)

## Zones

- **Normal zone (blue fill):** Price is within the inner bands (1 sigma). This area represents typical price movement around the mean.
- **Trending zone (orange fill):** Price is between the inner and outer bands. This suggests momentum is building or the asset is trending.
- **Extreme zone:** Price is outside the outer bands (2 sigma). This indicates a strong move or potential overextension.

## Inputs

- **BB Length:** Lookback period for SMA and standard deviation (default: 20)
- **Inner Multiplier:** Standard deviation multiplier for inner bands (default: 1.0)
- **Outer Multiplier:** Standard deviation multiplier for outer bands (default: 2.0)

## Usage

Watch for price transitioning between zones. A move from the normal zone into the trending zone can signal the start of a directional move. Price staying in the extreme zone may indicate a strong trend, while a return to the normal zone suggests mean reversion.

Volatility contraction (narrowing bands) often precedes a breakout, while expansion confirms increased volatility.
