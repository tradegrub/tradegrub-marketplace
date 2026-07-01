# Variance Ratio Test

![Concept](concept.svg)

Statistical test that measures whether price behavior resembles a random walk or a mean-reverting process. By comparing variance at different time scales, it identifies the current market regime so traders can select the appropriate strategy type.

## How It Works

- Computes log returns over a rolling window and calculates variance at a short period
- Aggregates returns over longer blocks and computes the variance ratio (long variance / scaled short variance)
- A ratio near 1.0 indicates random walk behavior, above 1.5 suggests trending, below 0.5 suggests mean reversion
- Smooths the ratio with a moving average to reduce noise and outputs a regime classification score
- Background shading highlights trending (green) and mean-reverting (red) regimes

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Short Period | 5 | 2-50 | Base variance calculation period |
| Long Period | 20 | 10-200 | Aggregated variance calculation period |
| Smoothing | 10 | 1-50 | SMA smoothing applied to ratio |
| Random Walk Upper | 1.5 | 1.0-3.0 | Threshold above which market is trending |
| Mean Reversion Lower | 0.5 | 0.1-1.0 | Threshold below which market is mean-reverting |

## Outputs

- **Variance Ratio**: Main oscillator line showing the ratio value
- **Regime**: Score of +1 (trending), 0 (random walk), or -1 (mean-reverting)
- **Background**: Green shading for trending, red for mean-reverting regimes

## Usage Notes

- Use to decide whether to apply trend-following or mean-reversion strategies in current conditions
- Values persistently above 1.0 favor momentum and breakout approaches
- Values persistently below 1.0 favor fading moves and range-bound strategies
