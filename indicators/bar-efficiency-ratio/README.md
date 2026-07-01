# Bar Efficiency Ratio

![Concept](concept.svg)

Measures how efficiently each bar moves in one direction. A ratio near 1.0 means the bar closed near its high or low (strong conviction). A ratio near 0 means a doji-like indecisive bar.

## How It Works

- Computes the ratio of absolute body size (close minus open) to the total bar range (high minus low)
- Applies a simple moving average for smoothing
- Plots both raw and smoothed values between 0 and 1

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Smooth Length | 10 | 2-50 | SMA period for the smoothed efficiency line |

## Outputs

- **Efficiency**: Purple raw efficiency ratio per bar
- **Smoothed**: Orange smoothed average
- **Directional**: Green dashed line at 0.7 (strong bars)
- **Indecisive**: Red dashed line at 0.3 (weak bars)

## Usage Notes

- Rising smoothed efficiency during a trend confirms strong conviction
- Declining efficiency at trend extremes warns of exhaustion
- Clusters of low-efficiency bars often precede breakouts
