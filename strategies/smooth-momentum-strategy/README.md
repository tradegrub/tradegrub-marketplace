## Smooth Momentum Strategy

Momentum zero-cross strategy using multi-stage cascaded smoothing for noise-free signals. Enters on zero-line crossover with slope confirmation.

### Parameters

- **Momentum Length**: Lookback for momentum (default: 14)
- **Smoothing Stages**: Number of smoothing passes (default: 3)
- **ATR Length**: ATR for stops (default: 14)
- **Stop/TP ATR Mult**: Risk management distances (default: 2.0/3.0)

### Signals

- **Long**: Smooth momentum crosses above zero with positive slope
- **Short**: Smooth momentum crosses below zero with negative slope
