# MA + RSI + Bollinger Bands

This triple-indicator strategy combines a moving average for trend direction, the Relative Strength Index for momentum filtering, and Bollinger Bands for pullback timing. The concept is simple but powerful: identify the trend with the MA, confirm momentum is not exhausted with RSI, and enter on a Bollinger Band touch that represents a pullback to value within the trend. This layered approach reduces false signals by requiring three independent confirmations before every entry.

## Conceptual Diagram

```
Price
 |  . . . BB Upper . . . . . . . . .
 | .   /\   .            .   /\  .
 |.   /  \   .    /\    .   /  \ .
 |   /    \  .   /  \  .   /    \.
 |  /      \ .  /    \.   /     .\
 |========= MA (trend) ============== SMA
 |  \      /. \      /.  \       .
 |   \    / .  \    / .    \     .
 |    \  /  .   \  /  .     \   .
 |     \/   .    \/   .      \ .
 |  . . BB Lower . . . . . . \. . .
 |                            ^
 |              Price hits lower BB + above MA + RSI ok
 +----------------------------------------------- Time
             BUY LONG         BUY LONG
         (pullback in uptrend, RSI not OB)
```

## How It Works

The strategy first establishes the trend using a 50-period SMA. When price is above the SMA, the market is in an uptrend; below it, a downtrend. This is the primary directional filter that determines whether long or short entries are considered.

Bollinger Bands (20-period, 2.0 standard deviations by default) provide the entry timing. In an uptrend, the strategy enters long when price touches or drops below the lower Bollinger Band, representing a pullback within the trend. In a downtrend, it enters short when price touches or rises above the upper Bollinger Band, representing a rally into resistance.

The RSI filter adds a critical momentum check. For longs, RSI must be below the overbought threshold (default 70), ensuring the entry is not at an exhaustion point. For shorts, RSI must be above the oversold threshold (default 30), ensuring the short entry is not into an oversold bounce. This prevents the strategy from entering when momentum has already pushed too far.

All three conditions are combined as vectorized boolean arrays and evaluated across every bar simultaneously. The strategy iterates through the combined signal to place entries, reversing between long and short as conditions flip.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Moving Average Length | 50 | 5-200 | SMA period for trend direction |
| RSI Length | 14 | 2-50 | RSI calculation period |
| RSI Overbought | 70 | 50-90 | Reject longs when RSI exceeds this |
| RSI Oversold | 30 | 10-50 | Reject shorts when RSI is below this |
| BB Length | 20 | 5-50 | Bollinger Bands lookback period |
| BB Multiplier | 2.0 | 0.5-4.0 | Standard deviation multiplier for bands |

## Python Advantage

Three independent indicators are combined into vectorized boolean conditions using numpy array broadcasting, evaluating every bar in a single expression:

```python
# Three indicators computed as full arrays
ma = ta.sma(close, ma_len)
rsi = ta.rsi(close, rsi_len)
bb_upper, bb_basis, bb_lower = ta.bb(close, bb_len, bb_mult)

# Compound conditions -- three filters in one boolean array
long_cond = (close > ma) & (rsi < rsi_ob) & (close <= bb_lower)
short_cond = (close < ma) & (rsi > rsi_os) & (close >= bb_upper)
```

Each condition is a numpy boolean array spanning all bars. The `&` operator performs element-wise AND, producing a final signal array where all three filters agree. Pine Script evaluates this logic one bar at a time and cannot reference the full condition array for analysis. The Python approach also enables quick parameter optimization by re-evaluating the boolean expressions with different thresholds without recomputing the underlying indicators.

## When to Use

This strategy works best on 4-hour and daily timeframes for large-cap stocks, index ETFs, and forex pairs that trend with periodic pullbacks. The Bollinger Band touch in an established trend represents high-probability mean reversion within the trend. Avoid using it in strongly trending markets where price rides the upper or lower band for extended periods (a "Bollinger Band walk"), as the RSI filter may block valid continuation entries.

## Risk Management

Place stops below the Bollinger Band at entry for longs, or above it for shorts, with a small ATR buffer. The expected profit target is the opposite Bollinger Band or the SMA, depending on how aggressively you want to capture the reversion move. Position sizing should factor in the width of the Bollinger Bands, as wider bands indicate higher volatility and require smaller positions.

## Combining with Other Indicators

- **MACD Crossover**: Use MACD direction to confirm the trend agrees with the MA filter before entering on BB touches.
- **Ichimoku Cloud**: Replace the simple MA trend filter with the Ichimoku cloud for a more nuanced trend assessment.
- **Pin Bar Reversal**: Look for pin bar candle patterns at the Bollinger Band touch for additional pattern confirmation.
