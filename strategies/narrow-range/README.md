# NR7 Narrow Range Breakout

A volatility contraction strategy based on the NR7 (Narrowest Range of 7) pattern, originally popularized by Toby Crabel in his work on short-term trading patterns. The core idea is that periods of compressed price action precede explosive moves. This strategy identifies bars with the narrowest high-low range over a lookback window, then trades the breakout direction on the following bar with ATR-based profit targets and stop losses.

## Conceptual Diagram

```
      ┃     ┃              NR Bar
     ┃┃    ┃┃    ┃┃        ┃┃  <-- Narrowest range of last 7
     ┃┃    ┃┃   ┃┃┃  ┃┃   ┃┃
    ┃┃┃   ┃┃┃   ┃┃   ┃┃┃  ┃┃   ┃┃
     ┃     ┃┃   ┃┃    ┃┃       ┃┃┃┃
            ┃                  ┃┃┃┃  <-- Breakout candle
     ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀ ┃┃┃┃───── 🟢 BUY
       (yellow highlight on     ┃┃      (close > NR high
        NR bar background)              + vol > avg x 1.3)

     ── TP: entry + ATR x 2.5 ──────────────────
     ── Entry ───────────────────────────────────
     ── SL: entry - ATR x 1.0 ──────────────────
```

## How It Works

On each bar, the strategy calculates the high-low range and compares it against the lowest range over the past N bars (default 7). When the current bar's range equals the minimum range in that window, it is flagged as a Narrow Range (NR) bar. These compression bars are highlighted with a subtle yellow background on the chart.

The actual trade occurs on the bar following the NR bar. If the closing price breaks above the NR bar's high, a long entry is triggered. If it breaks below the NR bar's low, a short entry fires. An optional volume filter requires that the breakout bar's volume exceeds a multiple of the 20-period average volume, confirming genuine participation behind the move.

Exits are managed with ATR-based targets and stops. The take-profit is set at 2.5 times ATR from the entry price, and the stop-loss at 1.0 times ATR. This gives the strategy a favorable 2.5:1 reward-to-risk ratio by default, though both multipliers are adjustable.

The strategy is designed around the principle that volatility is mean-reverting. Tight ranges cannot persist indefinitely, and the breakout direction after a squeeze tends to carry momentum. The volume filter helps distinguish genuine breakouts from low-conviction drift through the NR bar's boundaries.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| NR Period | 7 | 4 - 14 | Number of bars to compare for narrowest range detection |
| ATR Length | 14 | 5 - 50 | Lookback period for ATR calculation |
| ATR Take Profit Multiplier | 2.5 | 1.0 - 5.0 | ATR multiple for profit target |
| ATR Stop Loss Multiplier | 1.0 | 0.5 - 3.0 | ATR multiple for stop loss |
| Require Volume Surge | true | true/false | Whether to require above-average volume on breakout |
| Volume Surge Multiplier | 1.3 | 1.0 - 3.0 | Multiple of 20-period average volume required |

## Python Advantage

The NR detection uses vectorized comparison across the entire price history in a single operation, and the volume filter is applied as a boolean mask rather than a bar-by-bar conditional:

```python
bar_range = high - low
min_range = ta.lowest(bar_range, nr_period)
is_nr = bar_range <= min_range

avg_vol = ta.sma(volume, 20)
vol_surge = volume > avg_vol * vol_mult

nr_prev = np.roll(is_nr, 1)
long_signal = nr_prev & (close > prev_high) & vol_surge
```

This vectorized approach makes backtesting across thousands of bars instantaneous and allows easy experimentation with different NR periods and volume thresholds.

## When to Use

Ideal for intraday or daily charts on liquid stocks and ETFs that alternate between consolidation and expansion phases. Works especially well on instruments that exhibit clear volatility cycles. Avoid using on illiquid or thinly traded instruments where narrow ranges may simply reflect a lack of interest rather than genuine compression.

## Risk Management

The built-in ATR stop loss provides adaptive risk management that adjusts to current volatility. Keep the reward-to-risk ratio at 2:1 or higher by ensuring the take-profit multiplier exceeds the stop-loss multiplier. Position size based on the ATR stop distance so that each trade risks a consistent percentage of capital. Be aware that false breakouts are common after NR bars, which is why the volume confirmation filter exists. Disabling it increases signal frequency but reduces reliability.

## Combining with Other Indicators

- **Bollinger Band Width Squeeze**: Use BB width to confirm that broader volatility is also contracting, adding a second layer of squeeze confirmation before the NR breakout.
- **ADX Trend Filter**: Check ADX direction after the breakout to confirm the move has trending momentum behind it.
- **Mean Reversion ATR**: If the breakout fails and price reverses back inside the range, the mean reversion strategy can manage the counter-trade.
