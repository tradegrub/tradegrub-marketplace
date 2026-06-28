# EMA Distance Reversion

The EMA Distance strategy is a mean-reversion system that measures how far price has stretched from its exponential moving average, expressed as a percentage. When price extends beyond a configurable threshold in either direction, the strategy bets on a snap-back toward the mean. This approach is grounded in the statistical tendency of price to oscillate around its moving average, with extreme deviations creating high-probability reversion setups.

## Conceptual Diagram

```
 EMA Distance %
     │
 +3% ┄┄┄┄┄┄┄┄┄╱╲┄┄┄┄┄┄┄┄┄┄┄┄┄ Upper Threshold
     │        ╱  ╲
     │       ╱    ╲          ╱╲
     │      ╱      ╲        ╱  ╲
   0 ├─────╱────────╲──────╱────╲── EMA (zero line)
     │    ╱          ╲    ╱      ╲
     │   ╱            ╲  ╱        ╲
     │                 ╲╱          ╲
 -3% ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╲┄┄┄┄┄┄┄┄┄╲ Lower Threshold
     │                              ╲
     └──────────────────────────────── Time
              🔴         🟢         🟢
         Crosses above  Crosses    Crosses
         +3% = SHORT    below -3%  below -3%
         Exit near 0    = LONG     = LONG
                        Exit near 0
```

## How It Works

The strategy computes an EMA over the specified length (default 21) and then calculates the percentage distance between the current close and the EMA: `((close - ema) / ema) * 100`. This normalizes the distance to a percentage, making the threshold applicable across instruments with different price levels.

A long entry triggers when the distance crosses below the negative threshold (default -3.0%). This means price has fallen more than 3% below its EMA, representing an oversold condition relative to the recent trend. The crossing condition (current bar below threshold, previous bar above) ensures the entry occurs at the moment of threshold penetration rather than during an extended decline.

A short entry triggers symmetrically when the distance crosses above the positive threshold (+3.0%), indicating price has stretched too far above the EMA and is due for a pullback.

Exits target a return near the EMA. Long positions close when the distance crosses back above the negative exit threshold (default -0.5%), indicating price has reverted most of the way back to the mean. Short positions close when the distance drops below the positive exit threshold (+0.5%). The exit threshold is deliberately set close to zero but not exactly at zero, allowing the strategy to capture the bulk of the reversion move without waiting for a perfect mean touch.

The two-threshold system (entry and exit) creates an asymmetric trade structure where the entry requires an extreme deviation but the exit only requires a partial reversion, capturing the "easy" part of the mean reversion.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| EMA Length | 21 | 5-200 | Period for the exponential moving average |
| Distance Threshold % | 3.0 | 1.0-15.0 | Percentage distance from EMA required to trigger an entry |
| Exit Distance % | 0.5 | 0.0-5.0 | Percentage distance from EMA at which to close the position |

## Python Advantage

The strategy computes percentage distance as a vectorized array operation and uses bar-to-bar comparisons for threshold crossing detection.

```python
# Vectorized percentage distance — computed for all bars at once
ema = ta.ema(close, ema_length)
dist = ((close - ema) / ema) * 100

# Threshold crossing detection using consecutive bar indexing
# This is a manual crossunder: prev bar above threshold, current below
if dist[-1] < -distance_pct and dist[-2] >= -distance_pct:
    strategy.entry("Long", strategy.LONG)

# Partial reversion exit — doesn't wait for full mean touch
if dist[-1] > -exit_pct and dist[-2] <= -exit_pct:
    strategy.close("Long")
```

The percentage distance computation `((close - ema) / ema) * 100` operates on entire numpy arrays, producing a distance time series for every bar in a single expression. The manual crossing detection with `[-1]` and `[-2]` indexing provides precise control over the crossing direction without relying on a generic crossover function.

## When to Use

Best suited for instruments that exhibit rubber-band behavior around their moving averages. Works well on large-cap stocks, major index ETFs, and forex majors on daily and 4-hour timeframes. The 3% default threshold is calibrated for daily equity charts; adjust to 1-2% for intraday or to 5-10% for highly volatile instruments like small caps or crypto. Avoid during strong trending phases where price can stay extended from the EMA for weeks.

## Risk Management

The distance threshold defines the expected edge, but price can continue moving away from the EMA after entry. Place a hard stop at 2x the entry threshold distance (e.g., if entering at -3%, stop at -6%) to limit losses when the reversion fails. The exit threshold controls how much profit is captured: setting it to 0.0% targets a full mean reversion but risks giving back gains on a bounce. The default 0.5% strikes a balance between profit capture and exit reliability.

## Combining with Other Indicators

- **Bollinger Bands**: Combine EMA distance extremes with Bollinger Band touches for double-confirmation mean reversion entries.
- **Choppiness Filter**: Confirm the market is in a range-bound state (high choppiness) before trading mean reversion, avoiding trend-driven extensions that do not revert.
- **Doji Reversal**: Look for doji patterns at EMA distance extremes to add candlestick confirmation to the statistical reversion signal.
