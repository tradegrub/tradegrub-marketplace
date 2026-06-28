# Elder Triple Screen

The Elder Triple Screen is an implementation of Alexander Elder's renowned multi-layered trading system, first published in his 1993 book "Trading for a Living." The system applies three independent analytical screens, each using a different type of indicator, to filter trades through trend, momentum, and timing layers. Only when all three screens agree does the strategy enter a position, producing high-conviction signals that align short-term timing with the dominant trend direction.

## Conceptual Diagram

```
Screen 1: Trend (EMA Slope)
 |        ╱╱╱╱╱╱  EMA rising = UPTREND
 |  ╱╱╱╱╱╱
 | ╱
 +──────────────────────────────── Time

Screen 2: Momentum (MACD Histogram)
 |              /\
 |    hist     /  \   hist rising
 |    falling /    \  = momentum OK
 0 ──/\──────/──────\────────────
 |  /  \   /        \
 +──────────────────────────────── Time

Screen 3: Entry (Stochastic)
 80 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  Overbought
 |     /\          /\
 |    /  \   /\   /  \
 |   /    \ /  \ /    \
 20 ─ ─ ─ ─X─ ─ ─ ─ ─ ─ ─ ─ ─  Oversold
 +──────────────────────────────── Time
          🟢 BUY
    (trend UP + hist rising + stoch < 20)
```

## How It Works

Screen 1 determines the dominant trend direction using the slope of an exponential moving average. When the EMA is rising (current value exceeds the prior bar), the market is in an uptrend. When falling, it is in a downtrend. This acts as the master filter: long trades are only permitted in uptrends, short trades only in downtrends.

Screen 2 measures momentum using the MACD histogram (the difference between the MACD line and its signal line). The strategy checks whether the histogram is rising or falling via the `ta.change()` function. In an uptrend, the histogram must be rising, confirming that momentum is accelerating in the trend direction. In a downtrend, the histogram must be falling.

Screen 3 provides precise entry timing using the Stochastic oscillator, smoothed with a 3-period SMA. In uptrends, entries occur when the smoothed Stochastic dips below the oversold threshold (default 20), catching pullbacks within the trend. In downtrends, entries fire when the Stochastic rises above the overbought threshold (default 80), timing entries on counter-trend rallies.

The vectorized implementation processes all three screens simultaneously across the full price history, iterating through the combined boolean array to fire entries at every qualifying bar.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Trend EMA Length | 13 | 5 - 100 | EMA period for Screen 1 trend direction |
| MACD Fast | 12 | 2 - 50 | Fast EMA period for MACD calculation |
| MACD Slow | 26 | 10 - 100 | Slow EMA period for MACD calculation |
| MACD Signal | 9 | 2 - 30 | Signal line smoothing period for MACD |
| Stochastic Length | 14 | 2 - 50 | Lookback period for Stochastic %K |
| Stochastic Overbought | 80 | 60 - 95 | Upper threshold for short entry timing |
| Stochastic Oversold | 20 | 5 - 40 | Lower threshold for long entry timing |

## Python Advantage

The strategy computes five independent indicator arrays and combines them into a triple-screen condition using element-wise boolean operators:

```python
# Screen 1: Trend via EMA slope — vectorized change detection
ema_slope = ta.change(ema_trend, 1)
uptrend = ema_slope > 0

# Screen 2: Momentum via MACD histogram direction
hist_rising = ta.change(hist, 1) > 0

# Screen 3: Stochastic with SMA smoothing
stoch_smooth = ta.sma(stoch_k, 3)

# Triple-screen compound condition — three boolean arrays merged with &
long_cond = uptrend & hist_rising & (stoch_smooth < stoch_os)
short_cond = downtrend & hist_falling & (stoch_smooth > stoch_ob)
```

The `&` operator performs element-wise AND across three numpy boolean arrays, producing a single condition array that is True only where all three screens align. Pine Script evaluates conditions bar-by-bar and cannot pre-compute the full condition array or chain multiple indicator pipelines into a single composite boolean. The `ta.change()` wrapper computes first-differences across the entire array in one call.

## When to Use

Elder Triple Screen is designed for swing trading on daily charts, where the three screens simulate multi-timeframe analysis on a single timeframe. It works well on liquid stocks, index ETFs, and major forex pairs. The system is especially effective during trending markets with periodic pullbacks, as the Stochastic screen times entries on dips within the trend. Avoid during extended range-bound conditions where the EMA slope oscillates around zero.

## Risk Management

The strategy lacks explicit stop-loss logic, relying on signal reversal for exits. Consider placing stops below the swing low that corresponds to the Stochastic oversold dip for longs, or above the swing high for shorts. The triple-screen filter naturally reduces trade frequency, which limits overall exposure. Since the Stochastic screen requires extreme readings for entry, failed entries typically reverse quickly, keeping losses small if stops are tight.

## Combining with Other Indicators

- **Supertrend** provides a trailing stop exit that replaces the signal-reversal exit with adaptive protection.
- **RSI Divergence** adds divergence confirmation at the Stochastic extreme, strengthening the entry signal.
- **Squeeze Momentum** confirms that volatility expansion supports the momentum screen reading.
