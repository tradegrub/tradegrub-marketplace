## Dynamic RSI Strategy

Mean reversion strategy with dynamic overbought/oversold zones that adapt to volatility. In volatile markets, zones widen to filter noise; in calm markets, zones tighten for more signals.

### Parameters

- **Base RSI Length**: Base period for RSI (default: 14)
- **ATR Length**: ATR for stops and zone adaptation (default: 14)
- **Stop/TP ATR Mult**: Stop and take profit distances (default: 2.0/2.5)

### Signals

- **Long**: RSI crosses back above dynamic oversold zone
- **Short**: RSI crosses back below dynamic overbought zone
