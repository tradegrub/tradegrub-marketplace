## Complete Trade Planner

Full entry and exit framework combining RSI, MA trend, and MACD signals with configurable stop loss, take profit, and trailing stop. Requires multiple signal agreement for entry.

### Parameters

- **RSI/MA/ATR Length**: Indicator periods (default: 14, 20, 14)
- **Stop Loss ATR Mult**: Fixed stop distance (default: 2.0)
- **Take Profit ATR Mult**: Profit target distance (default: 3.0)
- **Trailing Stop ATR Mult**: Trailing stop distance (default: 1.5)
- **Min Signals**: Required signal agreement count (default: 2)

### Signals

- **Long**: Multiple indicators agree on bullish conditions
- **Short**: Multiple indicators agree on bearish conditions
- **Exit**: Fixed SL, fixed TP, or trailing stop (whichever hits first)
