## Directional Vortex Strategy

Vortex indicator crossover strategy with threshold-based filtering. Enters only when the vortex difference exceeds a minimum threshold for higher quality signals.

### Parameters

- **Vortex Length**: Vortex indicator period (default: 14)
- **ATR Length**: ATR period for stops (default: 14)
- **Stop/TP ATR Mult**: Stop and take profit distances (default: 2.0/3.0)
- **Cross Threshold**: Minimum VI+/VI- difference for entry (default: 0.1)

### Signals

- **Long**: VI+ minus VI- crosses above threshold
- **Short**: VI- minus VI+ crosses above threshold
