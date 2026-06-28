# Volatility Breakout

The Volatility Breakout strategy identifies periods of compressed volatility using Bollinger Band Width percentile analysis and trades the directional breakout when price expands beyond the bands during a squeeze state. Unlike simple band crossover strategies, this implementation requires that the bands are historically narrow before entering, filtering out the noise-driven touches that occur during normal volatility. The concept draws on the empirical observation that low-volatility periods reliably precede high-volatility expansions.

## Conceptual Diagram

```
Price
 |         · · Upper BB · · ·  · · · ·  · ·
 |    · · ·╱╲·              ·╱╲ ·
 |   ·   ╱╱  ╲·         · ╱╱   ╲·
 |  · · ╱╱    ╲ · ═══ · ╱╱      ╲·
 | ·  ╱╱╱      ╲·     ·╱╱        ╲·
 |·──╱╱──────────╲───·╱╱── Basis ──╲──
 |  ╱╱             ╲·╱╱              ╲
 | · · Lower BB · · ·╱ · · · · · · · ·
 +──────────────────────────────────── Time
     normal       SQUEEZE      BREAKOUT
     (no entry)   (bands narrow) (close > upper)
                    ░░░░░░░      🟢 BUY
                  BBW < 20th
                  percentile       🔴 EXIT
                                 (close < basis)

BBW
 |  ──────          ──────────────
 |        \        /
 |         \──────/  <- below percentile = squeeze
 +──────────────────────────────── Time
```

## How It Works

The strategy calculates Bollinger Bands (upper, basis, lower) and Bollinger Band Width (BBW) over a configurable period. BBW measures the distance between the bands as a percentage of the basis, quantifying current volatility relative to recent price levels. A 100-bar rolling window computes the minimum and maximum BBW values, establishing the recent volatility range.

A squeeze is detected when the current BBW falls below a percentile threshold of its recent range. Specifically, the threshold is calculated as `bbw_min + (bbw_max - bbw_min) * (squeeze_pctile / 100)`. When BBW is below this level, the market is in historically compressed volatility, signaling a coiled state primed for expansion.

Entry signals require two simultaneous conditions: the market must be in a squeeze AND price must close beyond the Bollinger Band. A long entry fires when price crosses above the upper band during a squeeze. A short entry fires when price crosses below the lower band during a squeeze. This dual requirement eliminates band touches during normal volatility that are more likely to be mean-reverting rather than breakout events.

Exits are dual-layered. The primary exit triggers when price crosses back to the basis line (middle band), indicating the breakout impulse has faded. A secondary ATR-based trailing stop provides disaster protection, calculated as ATR multiplied by the stop multiplier. Background highlighting marks squeeze periods in yellow for visual reference.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| BB Length | 20 | 10 - 50 | Bollinger Bands lookback period |
| BB Multiplier | 2.0 | 1.0 - 4.0 | Standard deviation multiplier for band width |
| Squeeze Percentile | 20.0 | 5.0 - 50.0 | BBW percentile threshold below which a squeeze is detected |
| ATR Length | 14 | 5 - 50 | Period for ATR trailing stop calculation |
| ATR Stop Multiplier | 1.5 | 0.5 - 4.0 | ATR multiple for trailing stop distance |

## Python Advantage

The strategy computes a rolling percentile-based squeeze threshold using vectorized array arithmetic, then combines it with crossover detection using the `&` operator:

```python
# Rolling BBW range for percentile computation — full-array operations
bbw_min = ta.lowest(bbw, 100)
bbw_max = ta.highest(bbw, 100)
bbw_range = bbw_max - bbw_min
bbw_threshold = bbw_min + bbw_range * (squeeze_pctile / 100.0)

# Vectorized squeeze detection — boolean array across full history
in_squeeze = bbw < bbw_threshold

# Compound breakout condition — crossover AND squeeze state
long_signal = ta.crossover(close, upper) & in_squeeze
short_signal = ta.crossunder(close, lower) & in_squeeze
```

The percentile threshold computation involves four numpy array operations chained together (`lowest`, `highest`, subtraction, multiplication), producing a dynamic threshold array that adapts across the full price history. The `&` operator merges the crossover boolean array with the squeeze boolean array element-wise. Pine Script would need to compute each value per-bar and cannot compose boolean arrays with `&`.

## When to Use

Volatility breakout strategies excel on instruments that cycle between consolidation and trending phases: crypto assets, small-cap stocks, commodity futures, and forex pairs around scheduled news events. Timeframes of 15 minutes to daily work best. The squeeze filter makes this strategy naturally patient, only trading when volatility compression signals a high-probability expansion. Lower the squeeze percentile to 10 for fewer but more extreme setups.

## Risk Management

The ATR trailing stop provides adaptive risk management that widens during volatile breakouts and tightens during calm conditions. Place initial hard stops at the opposite Bollinger Band at the time of entry. Breakout strategies have an inherent failure rate; not every squeeze produces a sustained trend. Size positions so that a stop-out represents no more than 1-2% of account equity. The basis-line exit captures the initial impulse without overstaying.

## Combining with Other Indicators

- **Squeeze Momentum** provides a Keltner-channel-based squeeze detection for cross-confirmation with the BBW percentile method.
- **Range Breakout** adds Donchian channel breakout confirmation to the Bollinger squeeze signal.
- **ADX Trend + RSI Momentum Filter** validates that the post-squeeze expansion has genuine trend strength behind it.
