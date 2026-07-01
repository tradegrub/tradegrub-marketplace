# Volatility Extreme Detector

Constructs a synthetic volatility measure from price range to detect both extreme bottoms and tops. The bottom detector measures how far the current low has fallen from the highest close, while the top detector measures how far the current high has risen from the lowest close. Signals fire when either reading exceeds its dynamic statistical threshold.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Lookback Period** (5-100, default 22): Window for highest/lowest close reference
- **Smoothing** (1-10, default 3): Moving average smoothing on raw readings
- **Extreme Threshold** (0.5-4.0, default 1.5): Standard deviations above mean to trigger signal

## Signals

- **Bottom Volatility** (green): Positive values, spikes indicate panic selling
- **Top Volatility** (red): Negative values, spikes indicate euphoric buying
- **Triangle markers**: Appear at statistical extremes
- **Background shading**: Highlights extreme periods

## Use Cases

- Identify capitulation bottoms without external volatility data
- Detect blow-off tops using the inverted measure
- Time entries after extreme volatility subsides
