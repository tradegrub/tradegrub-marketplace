# Three Bar Reversal

The Three Bar Reversal strategy identifies a classic candlestick pattern where the market overextends in one direction, fails to follow through, and then reverses sharply with a decisive close beyond the first bar's range. This pattern captures exhaustion points where one side of the market has fully committed and the other side takes control. The three-bar structure provides stronger confirmation than single-candle patterns like hammers or shooting stars.

## Conceptual Diagram

```
Bullish Three Bar Reversal:

Price
 |   Bar1     Bar2     Bar3
 |  (bear)   (lower)  (bull)
 |   ┌─┐                ┌─┐ <- Close above Bar1 high
 |   │ │      ┌─┐       │ │
 |   │X│      │ │       │ │
 |   │ │      │X│       │ │
 |   └─┘      │ │       │ │
 |             └─┘       └─┘
 |              |
 |         Lower low +
 |         lower close
 +──────────────────────────── Time
                         BUY
              STOP below Bar2 low
```

## How It Works

A bullish three-bar reversal requires three specific conditions across consecutive bars. Bar 1 must be bearish (close below open), establishing the existing downward pressure. Bar 2 must make both a lower low and a lower close than Bar 1, showing the selling pressure intensifying and trapping more shorts. Bar 3 must be bullish (close above open) and must close above Bar 1's high, demonstrating that buyers have overwhelmed the sellers and pushed price beyond the entire range of the initial bearish bar.

The bearish version mirrors this logic. Bar 1 must be bullish, Bar 2 must make a higher high and higher close, and Bar 3 must be bearish with a close below Bar 1's low. This traps buyers who entered during the extension and rewards sellers who fade the exhaustion.

Entries include both a stop-loss and profit target. The stop is placed beyond Bar 2's extreme (the lowest low for bullish setups, highest high for bearish) with a half-ATR buffer. The profit target is set at the entry price plus the ATR multiplied by the target multiplier, providing a defined risk-reward ratio for each trade.

A trend EMA is plotted for visual context, helping traders assess whether the reversal aligns with or opposes the broader trend direction.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| ATR Length | 14 | 5 - 50 | Lookback period for ATR used in stop and target calculations |
| ATR Target Multiplier | 2.0 | 1.0 - 5.0 | Multiplier applied to ATR for profit target distance |
| Trend EMA Length | 50 | 20 - 200 | EMA period plotted for trend context |

## Python Advantage

The multi-bar pattern detection uses Python's negative indexing to reference specific historical bars cleanly:

```python
# Direct negative indexing for multi-bar pattern detection
bar1_bear = close[-3] < open[-3]
bar2_lower = low[-2] < low[-3] and close[-2] < close[-3]
bar3_bull_close = close[-1] > open[-1] and close[-1] > high[-3]

bull_3bar = bar1_bear and bar2_lower and bar3_bull_close

# ATR-scaled stop and target in a single exit call
strategy.exit("Long Exit", "Long",
              stop=low[-2] - atr[-1] * 0.5,
              limit=close[-1] + atr[-1] * atr_mult)
```

Python's `[-3]`, `[-2]`, `[-1]` indexing makes the three-bar relationship immediately readable. The compound boolean `bull_3bar` collapses six conditions into a single variable. Pine Script requires separate `close[2]`, `close[1]`, `close[0]` references with confusing forward-looking index numbering.

## When to Use

Three-bar reversals are most effective on daily and weekly charts for swing trading at market turning points. The pattern is relatively rare but high-conviction, making it suitable as a standalone signal. It works best at the end of extended moves where momentum exhaustion is likely: stocks hitting resistance, futures at contract highs/lows, and forex pairs at round numbers.

## Risk Management

The built-in stop-loss below Bar 2's extreme with an ATR buffer provides defined risk per trade. The ATR target multiplier controls the reward-to-risk ratio; at the default of 2.0, each trade targets twice the ATR. Since the pattern requires three specific bars, there is no ambiguity about invalidation: if price breaks Bar 2's extreme, the reversal thesis is wrong.

## Combining with Other Indicators

- **RSI Divergence** adds momentum divergence confirmation at the reversal point, strengthening the signal.
- **VWAP Bounce** confirms the reversal occurs near institutional volume-weighted support or resistance.
- **Std Dev Channel** identifies whether the reversal happens at a statistically significant price extreme.
