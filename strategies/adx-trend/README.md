# ADX Trend

The ADX Trend strategy is a directional trend-following system built on Welles Wilder's Directional Movement Index. It enters long positions when the +DI crosses above -DI during a strong trend (ADX above threshold), and exits when the -DI crosses back above +DI. This is a long-only trend filter that avoids trading during weak or sideways markets by requiring ADX confirmation before committing capital.

## Conceptual Diagram

```
 ADX / DI Panel
  50 │                                +DI ───
     │         ╱╲                     -DI - - -
  40 │        ╱  ╲    ADX             ADX .....
     │   ....╱....╲..........
  25 ┄┄┄╱┄┄┄┄┄┄┄┄┄╲┄┄┄┄┄┄┄┄┄┄┄┄ Threshold
     │ ╱            ╲
  10 │╱              ╲───────
     │
     │  ──╲    ╱──╲        ╱──    +DI
     │     ╲  ╱    ╲      ╱
     │  ─ ─ ╲╱─ ─ ─╲─ ─╱─ ─ ─   -DI
     └──────────────────────────── Time
          🟢         🔴
       +DI > -DI   -DI crosses
       ADX > 25    above +DI
       ENTER LONG  CLOSE LONG
```

## How It Works

The strategy computes three lines from the Directional Movement Index: +DI (positive directional indicator), -DI (negative directional indicator), and ADX (the smoothed average of the absolute difference between +DI and -DI, normalized by their sum). ADX quantifies trend strength on a 0-100 scale regardless of direction, while the DI lines reveal which side controls the market.

A long entry triggers when two conditions coincide on the current bar: the +DI line crosses above the -DI line (a directional shift toward bullish control), and the ADX value exceeds the threshold (default 25), confirming that this directional move has meaningful strength behind it. Without the ADX filter, every DI crossover would generate a trade, including many false signals during sideways chop.

The exit is simpler and more conservative: any crossunder of +DI below -DI closes the long position immediately, regardless of the ADX level. This asymmetry between entry and exit is intentional. Entries demand strong trend confirmation, but exits act as a safety valve that does not wait for the trend to fully collapse before protecting capital.

The strategy is long-only by design. It does not take short positions, making it suitable for equity markets where short selling carries additional costs and risks. The ADX threshold acts as the primary risk control: higher thresholds produce fewer but higher-conviction trades.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| DI Length | 14 | 5-50 | Lookback period for computing +DI and -DI from directional movement |
| ADX Smoothing | 14 | 5-50 | Smoothing period applied to the ADX calculation |
| ADX Threshold | 25.0 | 15.0-50.0 | Minimum ADX value required to confirm trend strength for entry |

## Python Advantage

The strategy uses the `ta.dmi()` function to compute all three DMI components in a single vectorized call, returning numpy arrays for +DI, -DI, and ADX simultaneously.

```python
# Single call returns three numpy arrays — +DI, -DI, and ADX
plus_di, minus_di, adx_val = ta.dmi(high, low, close, di_len)

# Vectorized crossover detection on full array, index last bar
di_cross_up = ta.crossover(plus_di, minus_di)[-1]
di_cross_down = ta.crossunder(plus_di, minus_di)[-1]

# Boolean compound condition evaluated in one expression
if di_cross_up and strong_trend:
    strategy.entry("Long", strategy.LONG)
```

The tuple unpacking of `ta.dmi()` into three arrays enables clean, readable logic without intermediate variables or repeated function calls. Array indexing with `[-1]` provides direct access to the current bar value.

## When to Use

Best suited for trending markets on daily and 4-hour timeframes. Works well with stocks that exhibit strong momentum phases, trending forex pairs, and commodity futures. Avoid during earnings season or around major economic announcements where price action tends to whipsaw regardless of prior trend strength.

## Risk Management

The ADX threshold is the primary risk lever. Setting it to 30 or higher reduces the number of trades substantially but ensures entries only occur during powerful trends. Since the strategy has no built-in stop-loss, consider pairing it with an ATR-based stop or a fixed percentage stop. The exit on -DI crossover can sometimes lag during sharp reversals, so a supplementary trailing stop is recommended for volatile instruments.

## Combining with Other Indicators

- **ATR Trailing Stop**: Add a volatility-adjusted trailing stop to protect profits during the trend, since the DI crossover exit can lag.
- **EMA Crossover**: Use the EMA crossover for additional entry confirmation within the ADX-confirmed trend zone.
- **BB Width Squeeze**: Identify low-volatility consolidations before the ADX trend begins, timing entries at the start of the expansion.
