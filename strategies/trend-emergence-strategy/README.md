## Trend Emergence Strategy

Enters when the Aroon indicator signals trend emergence by crossing above a threshold with directional confirmation. Exits with ATR-based stops and targets.

### Parameters

- **Aroon Length**: Aroon indicator period (default: 25)
- **ATR Length**: ATR period for stops (default: 14)
- **Stop/TP ATR Mult**: Stop and take profit distances (default: 2.0/3.0)
- **Aroon Threshold**: Entry trigger level (default: 70)

### Signals

- **Long**: Aroon Up crosses above threshold and dominates Aroon Down
- **Short**: Aroon Down crosses above threshold and dominates Aroon Up
