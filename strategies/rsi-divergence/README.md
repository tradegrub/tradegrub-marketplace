# RSI Divergence

RSI Divergence is a mean reversion strategy that detects disagreements between price action and momentum. When price makes a new extreme but the Relative Strength Index fails to confirm it, the divergence signals weakening conviction in the current move. This concept, popularized by J. Welles Wilder and refined by Andrew Cardwell, is one of the most reliable reversal signals in technical analysis.

## Conceptual Diagram

```
Price
 |     /\
 |    /  \        /\
 |   /    \      /  \    Price: higher high
 |  /      \    /    \   but RSI: lower high
 | /        \  /      \          = BEARISH DIV
 |/          \/        \
 +──────────────────────────── Time

RSI
 70 ─ ─ ─╱╲─ ─ ─ ─ ─ ─ ─ ─ ─ Overbought
 |      /   \     /\
 |     /     \   /  \    RSI lower high
 50 ──/───────\─/────\──────── Midline (EXIT)
 |  /          \      \
 30 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ Oversold
 |                      \
 +──────────────────────────── Time
                SELL       EXIT
```

## How It Works

The strategy calculates RSI over a configurable period, then scans a lookback window for divergence patterns. A bullish divergence occurs when the current close equals or falls below the recent lowest close (price makes a lower low) while the current RSI reading is higher than the recent lowest RSI (RSI makes a higher low), and RSI is in oversold territory. This shows that sellers are losing momentum despite pushing price lower.

A bearish divergence is the mirror: price reaches a new high within the lookback window but RSI prints a lower high, and RSI is in overbought territory. Buying pressure is fading even as price continues to rise, warning of an impending reversal.

Exits trigger when RSI crosses the 50 midline. For long positions, this means RSI has recovered from oversold into neutral territory, capturing the mean reversion move. For shorts, RSI dropping below 50 signals the overbought condition has normalized.

The lookback parameter controls how many bars are scanned for the divergence comparison. Shorter lookbacks catch faster divergences; longer lookbacks find more significant structural divergences.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| RSI Length | 14 | 5 - 50 | Period for RSI calculation |
| Oversold Level | 30 | 10 - 40 | RSI threshold below which bullish divergences are valid |
| Overbought Level | 70 | 60 - 90 | RSI threshold above which bearish divergences are valid |
| Divergence Lookback | 5 | 2 - 20 | Number of bars to scan for divergence patterns |

## Python Advantage

The divergence detection uses rolling min/max lookups and multi-condition boolean logic that would be verbose in Pine Script:

```python
# Rolling extremes via vectorized lookback windows
price_low = ta.lowest(close, lookback)
price_high = ta.highest(close, lookback)
rsi_low = ta.lowest(rsi, lookback)
rsi_high = ta.highest(rsi, lookback)

# Multi-condition divergence detection — clean compound boolean
bullish_div = (close[-1] <= price_low[-1]) and \
              (rsi[-1] > rsi_low[-2]) and \
              (rsi[-1] < oversold)
```

Python's negative indexing (`[-1]`, `[-2]`) for bar references and compound boolean expressions with `and` operators make divergence logic readable. In Pine Script, detecting the "RSI made a higher low while price made a lower low" condition requires multiple `ta.valuewhen()` calls and nested `if` blocks.

## When to Use

Divergences are most effective on higher timeframes (4-hour, daily, weekly) where they reflect genuine shifts in institutional momentum rather than intrabar noise. They work well on trending instruments approaching exhaustion points: stocks at resistance, forex pairs at round numbers, and crypto near previous swing highs or lows.

## Risk Management

Divergences can persist for multiple bars before price reverses, so avoid over-sizing positions on the initial signal. Place stops below the lowest low of the divergence lookback for longs, or above the highest high for shorts. The RSI midline exit provides a natural profit target, but consider trailing stops for extended moves.

## Combining with Other Indicators

- **VWAP Bounce** adds institutional-level support/resistance confirmation to divergence signals.
- **Two Bar Reversal** or **Three Bar Reversal** provides candlestick pattern confirmation at the divergence point.
- **Std Dev Channel** identifies when divergences occur at statistically significant price levels.
