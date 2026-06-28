# ATR Range Expansion Breakout

The ATR Breakout strategy uses the Average True Range to construct dynamic volatility bands around a moving average, then trades breakouts beyond those bands. Unlike fixed-percentage channels, ATR bands expand and contract with market volatility, automatically adapting entry thresholds to current conditions. The concept builds on the observation that significant price moves often begin with a volatility expansion that pushes price beyond its normal range.

## Conceptual Diagram

```
Price
 │          · · Upper Band (MA + ATR x 1.5) · ·
 │        ·    ╱╲  ·
 │      ·    ╱    ╲  ·         ╱
 │    ·    ╱       ╲   ·     ╱
 │   ·   ╱          ╲   ·  ╱
 │  ════╱═══ Basis ══╄═══╱══════ MA(20)
 │     ╱              ╲╱
 │    ╱            ·  ╱  ·
 │   ╱           ·  ╱     ·
 │  ╱          ·   ╱        ·
 │ ╱         · · Lower Band (MA - ATR x 1.5)
 └──────────────────────────────── Time
    🟢 Cross        🔴 Cross    🟢 Cross
    above upper     below lower  above upper
```

## How It Works

The strategy calculates a simple moving average as the basis line, then adds and subtracts a multiple of ATR to create upper and lower breakout bands. When price crosses above the upper band, it signals that bullish momentum has exceeded normal volatility, triggering a long entry. When price crosses below the lower band, bearish momentum has overwhelmed normal range, triggering a short entry.

The entry multiplier (default 1.5) determines how far price must travel beyond the moving average before a breakout is confirmed. Higher multipliers filter out more noise but delay entries. The exit multiplier (default 1.0) creates a tighter band for exits, so positions are closed before price fully reverts to the basis.

Exit logic works on the opposite side: long positions close when price crosses below the lower exit band, and short positions close when price crosses above the upper exit band. This creates an asymmetry where entries require a larger move than exits, protecting profits by exiting sooner during reversals.

The ATR component makes this strategy self-adjusting. During high-volatility periods, the bands widen automatically, requiring a larger absolute price move to trigger a breakout. During low-volatility compression, the bands narrow, making it easier for price to break out when the next directional move begins.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| ATR Length | 14 | 5-50 | Lookback period for calculating Average True Range |
| ATR Breakout Multiplier | 1.5 | 0.5-4.0 | Multiple of ATR added/subtracted from MA for entry bands |
| MA Length | 20 | 5-100 | Period of the simple moving average used as the basis line |
| ATR Exit Multiplier | 1.0 | 0.5-3.0 | Tighter ATR multiple used for exit bands |

## Python Advantage

The strategy constructs dynamic bands and detects crossovers using fully vectorized array operations, then plots the bands with a filled region for visual clarity.

```python
# Vectorized band computation — entire history in one expression
upper_band = basis + atr * atr_mult
lower_band = basis - atr * atr_mult

# Crossover detection returns boolean arrays, not single values
long_signal = ta.crossover(close, upper_band)
short_signal = ta.crossunder(close, lower_band)

# Dual-band system: wider bands for entry, tighter for exit
exit_upper = basis + atr * exit_mult
exit_lower = basis - atr * exit_mult
```

Array arithmetic with `basis + atr * atr_mult` broadcasts the multiplication and addition across every bar simultaneously. The separate entry and exit multipliers create an asymmetric channel system that would require duplicate indicator instances in other scripting environments.

## When to Use

Works best on instruments that alternate between compression and expansion phases: individual stocks around earnings, forex pairs during session overlaps, and commodities responding to supply shocks. Daily and 4-hour timeframes provide the best balance between signal quality and trade frequency. Avoid during extended low-volatility regimes where ATR contracts to near-zero and bands collapse onto the basis.

## Risk Management

The exit band provides a built-in stop mechanism, but consider adding a fixed stop at 2x ATR from entry for catastrophic risk protection. Position size inversely to ATR: when ATR is high, reduce size since the bands are wide and potential loss per trade is larger. The entry multiplier directly controls risk: higher values mean fewer trades but each with stronger momentum confirmation behind it.

## Combining with Other Indicators

- **ADX Trend**: Confirm that a genuine trend is developing (ADX rising) before trusting the ATR breakout, filtering out false expansions during choppy markets.
- **BB Width Squeeze**: Use the Bollinger Band width squeeze to identify compression phases, then let the ATR breakout strategy time the expansion entry.
- **EMA Crossover**: Layer an EMA crossover as a trend direction filter so breakouts only trigger in the direction of the prevailing trend.
