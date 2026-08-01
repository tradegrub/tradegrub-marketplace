# Volumetric Candle Intensity

Normalizes each bar's volume against its rolling statistical baseline, then colors by both direction (bullish/bearish) and intensity (standard deviations above or below average). Higher intensity produces darker, more vivid colors while low-volume bars appear faded.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Volume Lookback** (5-100, default 20): Rolling window for mean and standard deviation
- **StdDev Multiplier** (0.5-3.0, default 1.0): Scales the standard deviation denominator

## Signals

- **Bright green bars**: High-volume bullish candles (strong buying)
- **Bright red bars**: High-volume bearish candles (strong selling)
- **Faded bars**: Below-average volume (low conviction)
- **Above +2 line**: Exceptional volume activity

## Use Cases

- Quickly identify which candles carry real volume conviction
- Filter breakouts by requiring high intensity
- Spot exhaustion when price moves on fading intensity
