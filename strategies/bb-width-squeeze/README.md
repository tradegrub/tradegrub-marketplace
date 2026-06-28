# BB Width Squeeze

The Bollinger Band Width Squeeze strategy detects periods of unusually low volatility by monitoring the width of Bollinger Bands, then trades the subsequent expansion breakout. The concept is rooted in the observation that volatility is cyclical: periods of tight consolidation (squeezes) are reliably followed by explosive directional moves. By measuring when band width reaches its lowest point over a lookback window, this strategy positions for the breakout before the crowd recognizes it.

## Conceptual Diagram

```
BB Width
 │╲
 │ ╲         ╱╲
 │  ╲       ╱  ╲         ╱╲
 │   ╲     ╱    ╲       ╱  ╲
 │    ╲   ╱      ╲     ╱    ╲
 │     ╲ ╱        ╲   ╱      ╲
 │      V──────────╲─╱────────╲── Squeeze Level
 │     ███ SQUEEZE  V  ███       (lowest x 1.05)
 └──────────────────────────────── Time

Price
 │                    ╱╲
 │            ╱╲     ╱  ╲
 │     ══════╱══╲═══╱════╲══════ Basis
 │          ╱    ╲ ╱      ╲
 │         ╱      V        ╲
 └──────────────────────────────── Time
          🟢              🔴
    Width expands     Width expands
    + close > basis   + close < basis
```

## How It Works

The strategy computes Bollinger Band width (BBW), which is the distance between the upper and lower bands divided by the basis. It then tracks the lowest BBW value over a configurable lookback period (default 50 bars). When the current BBW is within 5% of that historical minimum, the market is in a squeeze state, indicating that volatility has compressed to an extreme.

The entry trigger requires two conditions: the previous bar must have been in a squeeze state, and the current bar must show width expanding by at least 10% compared to the prior bar. This expansion signals that the squeeze is breaking and a directional move is beginning. The direction of the trade depends on where price sits relative to the basis: above the basis triggers a long entry, below triggers a short.

Exit conditions are straightforward mean-reversion targets. Long positions close when price crosses below the basis, and short positions close when price crosses above the basis. The logic assumes that the initial breakout momentum will carry price away from the basis, and a return to the basis represents profit-taking territory.

The 5% tolerance on the squeeze detection (`width_min * 1.05`) prevents the strategy from requiring an exact match to the historical low, which would rarely trigger. The 10% expansion requirement filters out minor width fluctuations that do not represent genuine breakouts.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| BB Length | 20 | 5-200 | Period for the Bollinger Band calculation |
| BB Multiplier | 2.0 | 0.5-5.0 | Standard deviation multiplier for the bands |
| Squeeze Threshold | 0.02 | 0.005-0.1 | Minimum BB width value (not used directly in current logic) |
| Width Lookback | 50 | 10-200 | Number of bars to search for the historical width minimum |

## Python Advantage

The strategy uses vectorized comparison operators and array indexing to detect squeeze states across the full history, then checks expansion conditions with simple bar-to-bar comparisons.

```python
# Vectorized squeeze detection — boolean array for every bar
width_min = ta.lowest(bb_width, lookback)
is_squeeze = bb_width <= width_min * 1.05

# Expansion detection: 10% width increase bar-over-bar
expanding = bb_width[-1] > bb_width[-2] * 1.1

# Two-bar pattern: squeeze on prior bar, expansion on current
if is_squeeze[-2] and expanding:
    if close[-1] > basis[-1]:
        strategy.entry("Long", strategy.LONG)
    else:
        strategy.entry("Short", strategy.SHORT)
```

The `is_squeeze` array is computed for every bar simultaneously using element-wise comparison with the rolling minimum. The `[-2]` and `[-1]` indexing enables clean two-bar pattern detection without loop state management.

## When to Use

Excels on instruments that exhibit clear compression-expansion cycles: individual stocks consolidating before earnings moves, forex pairs during quiet Asian sessions before London/New York opens, and commodities building bases before trend resumptions. Daily and 4-hour timeframes work best. The strategy generates infrequent but high-conviction signals, making it suitable for patient traders. Avoid on instruments with persistently low volatility where squeezes never resolve into meaningful breakouts.

## Risk Management

Place stops on the opposite side of the basis from the entry. For long entries, stop below the lower Bollinger Band at the point of squeeze; for shorts, stop above the upper band. The squeeze itself defines risk: if the breakout immediately reverses back into the squeeze zone, the thesis is invalidated. Position size should be larger than normal since squeeze breakouts offer favorable risk-reward ratios, but always cap exposure in case of false breakouts.

## Combining with Other Indicators

- **ADX Trend**: Confirm that ADX is rising during the expansion phase, validating that a genuine trend is forming rather than a false breakout.
- **EMA Volume Breakout**: Add volume confirmation to the squeeze breakout. A width expansion accompanied by a volume surge provides stronger conviction.
- **ATR Breakout**: Use ATR expansion as a secondary volatility confirmation alongside the BB width squeeze for double-filtered breakout signals.
