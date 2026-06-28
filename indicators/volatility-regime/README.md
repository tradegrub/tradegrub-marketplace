# Volatility Regime

The Volatility Regime indicator combines ATR percentile and Bollinger Band Width percentile into a composite score that classifies the current volatility environment as high, low, or neutral. By using two mathematically distinct volatility measures and ranking each against its own history, the indicator provides a more reliable regime classification than either metric alone, enabling traders to adapt position sizing, strategy selection, and stop placement to current market conditions.

## Conceptual Diagram

```text
Percentile
 │
100│
   │           ╱╲
 80│┄┄┄┄┄┄┄┄┄╱┄┄╲┄┄┄┄┄┄┄┄┄┄┄┄┄┄ High Volatility
   │    ╱╲   ╱    ╲         ╱╲
   │   ╱  ╲ ╱      ╲       ╱  ╲   ATR Pctl ───
   │  ╱    ╳        ╲     ╱    ╲   BBW Pctl - - -
 50│─╱───╱──╲────────╲───╱──────╲─ Regime ···
   │╱   ╱    ╲        ╲ ╱       ╲
   │   ╱      ╲        ╳         ╲
   │  ╱        ╲      ╱ ╲         ╲
 20│┄╱┄┄┄┄┄┄┄┄┄╲┄┄┄┄╱┄┄┄╲┄┄┄┄┄┄┄┄ Low Volatility
   │╱            ╲  ╱     ╲
  0│              ╲╱       ╲
   └──────────────────────────────── Time
    ░░ Low Vol ░░  ▓ High ▓  ░░ Low (squeeze)
    (squeeze)      (expansion)
```

## How It Works

The indicator computes two independent volatility measures. ATR (Average True Range, default 14-period) captures bar-by-bar volatility through the true range of each bar. Bollinger Band Width (default 20-period with 2.0 standard deviation multiplier) measures the spread between upper and lower Bollinger Bands as a percentage of the middle band, capturing price dispersion around the mean.

Each measure is ranked against its own recent history using percentile ranking over a configurable lookback (default 100 bars). ATR percentile tells you where current bar-level volatility sits relative to recent history. BBW percentile tells you where current price dispersion sits relative to recent history. Both produce 0-100 readings where 90 means "more volatile than 90% of the lookback period."

The two percentiles are averaged to produce the composite volatility regime score. This averaging exploits the low correlation between ATR (which measures range) and BBW (which measures dispersion). When both agree on high volatility, the signal is especially reliable. When they diverge, the composite remains moderate, avoiding false regime classifications.

Background shading highlights extreme regimes. Readings above 80 indicate a high-volatility regime (red shading) where ranges are wide, bands are expanded, and risk per trade is elevated. Readings below 20 indicate a low-volatility regime (green shading) that often precedes breakouts as the market compresses before releasing energy.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| ATR Length | 14 | 5 - 50 | Lookback period for ATR calculation |
| BB Length | 20 | 10 - 50 | Lookback period for Bollinger Band Width |
| BB Multiplier | 2.0 | 1.0 - 4.0 | Standard deviation multiplier for Bollinger Bands |
| Percentile Lookback | 100 | 20 - 500 | Period for percentile ranking of both measures |

## Python Advantage

The dual-percentile computation and composite scoring are expressed as chained vectorized operations, combining two independent volatility measures into a single regime score across all bars simultaneously:

```python
# Two independent volatility measures as full arrays
atr_val = ta.atr(high, low, close, atr_len)
bbw_val = ta.bbw(close, bb_len, bb_mult)

# Percentile ranking of each — full history in one call each
atr_pct = ta.percentrank(atr_val, pct_len)
bbw_pct = ta.percentrank(bbw_val, pct_len)

# Composite regime score: average of two percentile arrays
vol_regime = (atr_pct + bbw_pct) / 2

# Boolean masking for regime highlighting
bgcolor(vol_regime > 80, color="rgba(239,83,80,0.08)")
bgcolor(vol_regime < 20, color="rgba(38,166,154,0.08)")
```

Each `ta.percentrank` call ranks the entire volatility series against its rolling history in a single vectorized pass. The composite averaging and boolean comparisons are all array operations. In Python, you could extend this to a three-factor model by adding `ta.percentrank(ta.stdev(close, 20), pct_len)` and changing the divisor to 3, or use `np.select` for multi-tier regime classification (very low, low, neutral, high, very high).

## When to Use

The Volatility Regime indicator works on all timeframes and asset classes. It is most valuable on daily charts as a strategy selection filter. Low-volatility regimes (score below 20) are ideal for breakout strategies with tight stops, as compressed markets tend to produce explosive moves. High-volatility regimes (score above 80) call for wider stops, smaller positions, and mean-reversion approaches.

## Risk Management

Scale position sizes inversely to the regime score: smaller positions during high-volatility regimes, larger during low-volatility periods where risk is well-defined. During regime transitions (score crossing through 50), be cautious as the market is shifting character and historical patterns may not hold. Do not assume low-volatility regimes will break out immediately; compression can persist for extended periods before releasing.

## Combining with Other Indicators

- **ATR Percent**: Use ATR Percent for granular bar-level volatility measurement alongside the broader Volatility Regime score for percentile-based context.
- **Market Regime**: Cross-reference volatility regime with market regime to distinguish between four states: trending-volatile, trending-quiet, ranging-volatile, and ranging-quiet, each requiring a different strategy approach.
- **Range Indicator**: The Range Indicator's percentile output provides a complementary view focused on N-bar envelope width, which can diverge from ATR-based volatility during trending moves.
