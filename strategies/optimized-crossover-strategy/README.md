## Optimized Crossover Strategy

Walk-forward optimized MA crossover that periodically re-optimizes the fast/slow periods using scipy optimization on the training window.

### Parameters

- **Training Window**: Bars used for optimization (default: 100)
- **Re-optimize Every**: Bars between re-optimizations (default: 50)
- **ATR Length**: ATR for stops (default: 14)
- **Stop ATR Mult**: Stop distance (default: 2.0)

### Signals

- **Long/Short**: Optimized MA crossover signals
- **Walk-forward**: Periods adapt to recent market conditions
