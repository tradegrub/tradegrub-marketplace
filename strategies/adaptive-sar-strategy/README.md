## Adaptive SAR Strategy

Trend-following strategy using a parabolic SAR with volatility-adaptive acceleration factor. The AF maximum adjusts based on ATR percentile, speeding up in volatile markets.

### Parameters

- **AF Start/Max**: Acceleration factor range (default: 0.02 to 0.2)
- **ATR Length**: ATR period for volatility measurement (default: 14)
- **Stop ATR Multiple**: Stop loss distance in ATR units (default: 2.0)

### Signals

- **Long entry**: Price crosses above adaptive SAR
- **Short entry**: Price crosses below adaptive SAR
- **Stops**: ATR-based stop loss
