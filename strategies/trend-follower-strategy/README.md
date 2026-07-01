## Trend Follower Strategy

Dynamic SuperTrend strategy with a self-adjusting ATR multiplier. The multiplier widens in volatile markets and tightens in calm ones.

### Parameters

- **ATR Length**: ATR period (default: 10)
- **Base Multiplier**: Base ATR multiplier for trend bands (default: 3.0)
- **Take Profit ATR Mult**: Take profit distance in ATR units (default: 3.0)

### Signals

- **Long**: Price breaks above dynamic upper band
- **Short**: Price breaks below dynamic lower band
- **Trailing stop**: Dynamic trend line acts as trailing stop
