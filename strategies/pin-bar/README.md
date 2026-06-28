# Pin Bar Reversal

A candlestick pattern recognition strategy that identifies pin bars, single-candle reversal signals characterized by a long tail (wick) and a small body. Pin bars indicate rejection of a price level, and this strategy trades the expected reversal when they appear in the context of the prevailing trend. The concept originates from Japanese candlestick analysis and is one of the most widely followed price action patterns.

## Conceptual Diagram

```
                 Bearish Pin Bar
                     |  <-- Long upper wick (>60% of range)
                     |
                     |
  Trend SMA --------.|.---------------------------
                    [=]  <-- Small body (<33% of range)
                         close > SMA = valid context
                         🔴 SELL

     ─────────────────────────────────────────

                    [=]  <-- Small body (<33% of range)
  Trend SMA --------.|.---------------------------
                     |       close < SMA = valid context
                     |
                     |  <-- Long lower wick (>60% of range)
                 Bullish Pin Bar
                         🟢 BUY
```

## How It Works

The strategy decomposes each candle into three components: the body size (absolute difference between open and close), the upper wick (high minus the greater of open and close), and the lower wick (the lesser of open and close minus the low). Each component is expressed as a ratio of the total candle range (high minus low).

A bullish pin bar is identified when the body ratio is at or below the nose ratio threshold (default 33%) and the lower wick ratio meets or exceeds the tail ratio threshold (default 60%). This shape shows that sellers pushed price down aggressively but buyers rejected the lower level and drove price back up, leaving a long lower shadow. Additionally, the close must be below the trend SMA, confirming that the pin bar occurred in a downtrend context where a reversal is meaningful.

A bearish pin bar requires the same small body ratio but with the upper wick meeting the tail threshold. The close must be above the trend SMA, indicating the pin bar formed in an uptrend where exhaustion is likely.

Exits use ATR-based targets and stops. The stop loss is placed just beyond the tail of the pin bar (0.3x ATR past the extreme), and the take profit target is set at a configurable ATR multiple (default 2.0x) from the entry price. This tight stop beyond the rejection tail combined with a wider target creates a favorable risk-reward profile.

The trend SMA serves as a contextual filter. Without it, pin bars would fire in both trending and ranging conditions, leading to many false reversals. By requiring the close to be on the "overextended" side of the SMA, the strategy focuses on mean-reversion setups.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| ATR Length | 14 | 5 - 50 | Lookback period for ATR calculation |
| ATR Target Multiplier | 2.0 | 1.0 - 5.0 | ATR multiple for take profit target |
| Max Nose Ratio | 0.33 | 0.1 - 0.5 | Maximum body size as fraction of candle range |
| Min Tail Ratio | 0.60 | 0.4 - 0.8 | Minimum tail (wick) size as fraction of candle range |
| Trend SMA Length | 20 | 10 - 50 | Lookback for the trend context SMA |

## Python Advantage

Python's NumPy array operations allow the candle decomposition and ratio calculations to run across the entire dataset in a single pass. The conditional logic for body and wick ratios is clean and easy to adjust:

```python
body = np.abs(close - open)
candle_range = high - low
upper_wick = high - np.maximum(close, open)
lower_wick = np.minimum(close, open) - low

body_ratio = np.where(candle_range > 0, body / candle_range, 1.0)
upper_ratio = np.where(candle_range > 0, upper_wick / candle_range, 0)
lower_ratio = np.where(candle_range > 0, lower_wick / candle_range, 0)
```

The `np.where` guard against zero-range bars (dojis with identical high and low) prevents division-by-zero errors without needing verbose conditional branches.

## When to Use

Pin bars work best on daily and 4-hour charts where each candle represents significant price action. The pattern is effective on forex pairs, large-cap stocks, and commodity futures. Avoid low timeframes (1-minute, 5-minute) where pin bars form frequently from noise. The strategy performs best in trending markets that are due for pullback reversals, not in extended sideways consolidation.

## Risk Management

The stop loss is placed 0.3x ATR beyond the pin bar's tail, which is the natural invalidation level. If price pushes past the rejection point, the pin bar thesis is broken. Keep the ATR target multiplier at 2.0 or higher to maintain at least a 2:1 reward-to-risk ratio. Pin bars have a moderate hit rate (typically 45-55%), so the edge comes from the favorable ratio, not win frequency. Size positions so that the stop distance represents no more than 1-2% of account equity.

## Combining with Other Indicators

- **RSI Divergence**: A pin bar forming at a support level with bullish RSI divergence significantly increases the reversal probability.
- **Bollinger Bands**: Pin bars that touch or pierce the outer Bollinger Band represent price rejection at a statistical extreme, adding confluence.
- **Pivot Breakout**: Use pivot levels as the support/resistance context for pin bar formation. A pin bar at a pivot level is a higher-probability setup.
