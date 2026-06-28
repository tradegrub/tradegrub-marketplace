# Hammer Reversal

The Hammer Reversal strategy identifies hammer and shooting star candlestick patterns within trending contexts and enters trades with ATR-based stop-losses and profit targets. A hammer features a small body at the top of the candle with a long lower wick, indicating that sellers pushed price down but buyers drove it back up by the close. A shooting star is the inverse: a small body at the bottom with a long upper wick, showing rejected buying pressure. These single-bar patterns are among the most traded reversal signals in candlestick analysis.

## Conceptual Diagram

```
 Downtrend (below SMA)         Uptrend (above SMA)

 │╲                            │         ╱
 │ ╲                           │        ╱
 │  ╲    ┌┐ Hammer             │   ┌┐  ╱
 │   ╲   ├┤ (small body top)   │   │┤ ╱  Shooting Star
 │    ╲  │ │                   │   │ │    (small body bottom)
 │     ╲ │ │ long lower wick   │   ├┐    long upper wick
 │      ╲│ │                   │   ││
 │       └┘      ╱             │   └┘╲
 │              ╱              │      ╲
 │─ ─ ─ ─SMA─╱─ ─ ─ ─ ─ ─ ─ ─│─SMA─ ─╲─ ─ ─ ─
 │           ╱                 │        ╲
 │          ╱                  │         ╲
 └──────────────────────────────────────── Time
         🟢                           🔴
    Hammer below SMA          Shooting star above SMA
    = LONG reversal           = SHORT reversal
    Stop: below low           Stop: above high
    Target: close + ATR x 1.5 Target: close - ATR x 1.5
```

## How It Works

The strategy computes candlestick anatomy using numpy operations: body size (absolute difference between close and open), upper wick (high minus the greater of close and open), and lower wick (the lesser of close and open minus the low). These geometric components define the candle's shape.

A hammer is identified when: (1) the lower wick is at least 2x the body size (configurable via wick ratio), (2) the upper wick is less than half the body, (3) the body is non-zero, and (4) the close is below the trend SMA (default 20 periods), confirming a downtrend context. The long lower wick shows that sellers attempted to push price lower but were overwhelmed by buyers, suggesting exhaustion of selling pressure.

A shooting star requires: (1) the upper wick is at least 2x the body, (2) the lower wick is less than half the body, (3) the body is non-zero, and (4) the close is above the trend SMA, confirming an uptrend. The long upper wick reveals that buyers tried to push higher but failed, with sellers driving price back down.

Upon entry, the strategy places both a stop-loss and a profit target. For hammers, the stop is half an ATR below the candle's low, and the target is the close plus 1.5x ATR. For shooting stars, the stop is half an ATR above the high, and the target is the close minus 1.5x ATR. This creates a defined risk-reward structure on every trade.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| ATR Length | 14 | 5-50 | Period for ATR used in stops and targets |
| ATR Stop Multiplier | 1.5 | 0.5-5.0 | Multiple of ATR for the profit target distance |
| Min Wick-to-Body Ratio | 2.0 | 1.5-5.0 | Minimum ratio of the signal wick to body size |
| Trend SMA Length | 20 | 10-50 | Moving average period for trend direction context |

## Python Advantage

The strategy uses `np.maximum` and `np.minimum` for vectorized wick computation and combines four boolean conditions for pattern classification.

```python
# Vectorized candlestick geometry using numpy element-wise functions
body = np.abs(close - open)
upper_wick = high - np.maximum(close, open)
lower_wick = np.minimum(close, open) - low

# Hammer detection: four conditions in one compound expression
is_hammer = ((lower_wick[-1] > body[-1] * wick_ratio) and
             (upper_wick[-1] < body[-1] * 0.5) and
             (body[-1] > 0) and
             (close[-1] < trend_sma[-1]))

# Bracket order: stop + target from ATR
if is_hammer:
    strategy.entry("Long", strategy.LONG)
    strategy.exit("Long SL", "Long",
                  stop=low[-1] - atr[-1] * 0.5,
                  limit=close[-1] + atr[-1] * atr_mult)
```

The `np.maximum` and `np.minimum` functions compute element-wise max/min across full arrays, correctly identifying the body top and bottom regardless of whether the candle is bullish or bearish. This vectorized approach replaces the conditional logic (if bullish then body_top = close else body_top = open) that other languages require.

## When to Use

Best on daily and 4-hour timeframes where single-candle patterns have reliable follow-through. Effective on liquid stocks at support/resistance levels, forex pairs at round numbers, and any instrument with clean candlestick data. The trend context filter (SMA) ensures hammers only trigger in downtrends and shooting stars only in uptrends, which is where reversal patterns have their statistical edge. Avoid on very short timeframes (1-minute, 5-minute) where candle noise overwhelms pattern significance.

## Risk Management

The built-in stop and target create a defined risk-reward trade. The default setup offers roughly a 3:1 reward-to-risk ratio (1.5 ATR target vs 0.5 ATR stop). The wick ratio parameter controls pattern quality: higher ratios (3.0+) require more extreme wick extensions, producing fewer but higher-conviction signals. Always verify that the pattern occurs at a meaningful price level (prior support/resistance, round number, or moving average) rather than in the middle of a range.

## Combining with Other Indicators

- **Bollinger Band Bounce**: Hammers at the lower Bollinger Band or shooting stars at the upper band combine candlestick and statistical reversion signals.
- **Doji Reversal**: Use the doji strategy as a complementary signal. Hammers and dojis at the same support level within a few bars provide strong reversal confluence.
- **EMA Distance**: Confirm that price is stretched from its EMA when the hammer or shooting star forms, adding quantitative support to the visual pattern.
