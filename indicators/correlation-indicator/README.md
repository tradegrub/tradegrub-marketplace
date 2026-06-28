# Price-Volume Correlation

The Price-Volume Correlation indicator calculates a rolling Pearson correlation coefficient between closing price and volume, quantifying whether price moves are confirmed by corresponding volume shifts. Rooted in the Dow Theory principle that volume should confirm trends, this indicator provides a statistical measure of that relationship rather than relying on visual inspection alone.

## Conceptual Diagram

```
Corr
 │
+1.0 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ Perfect Positive
+0.7 ─ ─ ─ ─╱╲─ ─ ─ ─ ─ ─ ─ ─ ─ High Corr
 │      ╱╲  ╱  ╲          ╱╲
 │     ╱  ╲╱    ╲   ╱╲   ╱  ╲
+0.3  ╱          ╲ ╱  ╲ ╱    ╲
 │   ╱            ╳    ╳      ╲
 0.0─╱─ ─ ─ ─ ─ ╱─╲──╱─╲─ ─ ─╲─ Zero
 │              ╱   ╲╱   ╲     ╲
-0.3           ╱          ╲     ╲
 │            ╱            ╲     ╲
-0.7 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─╲─ ─ ╲ Low Corr
-1.0 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╲┄┄┄┄ Perfect Negative
 └──────────────────────────────── Time
      Confirmed     Diverging   Confirmed
      uptrend       volume      selling
```

## How It Works

The indicator computes a rolling Pearson correlation coefficient between the close price series and the volume series over the specified window (default 20 bars). The coefficient ranges from -1 to +1, where +1 means price and volume move in perfect lockstep, -1 means they move in opposite directions, and 0 indicates no linear relationship.

A 5-period SMA is applied to the raw correlation to produce a signal line that smooths out noise and reveals the underlying trend of the price-volume relationship. Horizontal reference lines are drawn at the user-defined high and low correlation thresholds (default +0.7 and -0.7).

When correlation is strongly positive during an uptrend, it confirms that buyers are stepping in with increasing conviction as price rises. When correlation turns negative during an uptrend, it warns of potential distribution where price is rising on declining volume. Background shading highlights periods when correlation exceeds the high or low thresholds, drawing immediate visual attention to significant regimes.

The indicator is particularly useful for detecting divergences. If price makes new highs but the correlation coefficient is falling, it suggests the trend is losing volume support, a classic precursor to reversals. Conversely, negative correlation during a downtrend that begins reverting toward zero can signal exhaustion of selling pressure.

## Parameters

| Parameter        | Default | Range        | Description                                             |
|------------------|---------|--------------|---------------------------------------------------------|
| Length           | 20      | 5 - 200      | Rolling window for the Pearson correlation calculation  |
| High Correlation | 0.7     | 0.3 - 1.0   | Threshold for strong positive correlation highlighting  |
| Low Correlation  | -0.7    | -1.0 to -0.3 | Threshold for strong negative correlation highlighting |

## Python Advantage

Python's statistical libraries make Pearson correlation a first-class operation on entire arrays. The boolean masking for background shading operates on complete arrays in a single pass:

```python
# Rolling Pearson correlation between price and volume — full array
corr = ta.correlation(close, volume, length)
corr_sma = ta.sma(corr, 5)

# Boolean array masking for background highlighting
bgcolor(corr > high_corr, color="rgba(102,187,106,0.06)")
bgcolor(corr < low_corr, color="rgba(239,83,80,0.06)")
```

The comparison `corr > high_corr` produces a boolean array across all bars simultaneously. In Pine Script, this requires conditional ternary logic evaluated bar-by-bar. Python lets you chain arbitrary statistical functions on the correlation output, such as `np.percentile(corr, 90)` for percentile ranking of correlation itself, or `ta.stdev(corr, 20)` to measure the volatility of the correlation signal, with zero additional loop overhead.

## When to Use

Price-Volume Correlation works best on liquid instruments where volume data is meaningful: equities, ETFs, and futures. It is less reliable on thinly traded assets or forex pairs where tick volume is a proxy. Use it on daily or 4-hour timeframes for swing trading confirmation, or on intraday charts to validate momentum during active sessions.

## Risk Management

Never use correlation readings alone as entry signals. Strong positive correlation confirms an existing trend but does not predict reversals by itself. When correlation drops sharply from high levels, tighten stops rather than reversing immediately. Low-correlation environments (readings near zero) indicate that volume provides no directional information, so rely on other indicators during those periods.

## Combining with Other Indicators

- **Momentum Composite**: When the Momentum Composite shows overbought readings and correlation is declining, the convergence of signals strengthens the reversal case.
- **Volume Profile POC**: Use correlation readings to validate whether price is gravitating toward or away from the Point of Control with volume support.
- **Trend Strength**: Cross-reference trend strength scores with correlation to confirm that strong trends have genuine volume participation.
