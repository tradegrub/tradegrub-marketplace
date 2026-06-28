# Choppiness Filter + EMA Trend

The Choppiness Index Filter combines the Choppiness Index (CHOP) with an EMA crossover system to solve a persistent problem in trend trading: entering during sideways, choppy markets. The Choppiness Index, developed by E.W. Dreiss, measures whether the market is trending or range-bound on a scale from 0 to 100. This strategy only permits EMA crossover trades when CHOP confirms a trending environment, and closes all positions when choppiness exceeds the 61.8 Fibonacci level.

## Conceptual Diagram

```
 CHOP
 100 │
 61.8┄┄┄┄┄┄╱╲┄┄┄┄┄┄┄┄┄┄┄┄╱╲┄┄┄ Choppy (close all)
     │    ╱  ╲            ╱  ╲
  50 ─ ─╱─ ─ ╲─ ─ ─ ─ ─╱─ ─ ╲─ Threshold
     │ ╱      ╲    ╱╲  ╱      ╲
     │╱        ╲  ╱  ╲╱        ╲
   0 │          ╲╱                Trending
     └──────────────────────────── Time
       ✗ Chop   ✓ Trend  ✗ Chop   ✓

 EMA Panel (only active when CHOP < 50)
     │         ╱╲         Fast ───
     │    ╱╲  ╱  ╲        Slow - - -
     │   ╱  ╲╱    ╲
     │  ╱  ╱╲      ╲         ╱
     │─╱──╱──╲──────╲───────╱──
     └──────────────────────────── Time
          🟢          🔴       🟢
```

## How It Works

The Choppiness Index is calculated using the ATR and the high-low range over a lookback period. It measures how much of the total range has been consumed by directionless movement. Values above 61.8 indicate highly choppy, sideways conditions. Values below 50 indicate a trending market. The zone between 50 and 61.8 is transitional.

When the Choppiness Index is below the threshold (default 50), the strategy considers the market to be trending and activates the EMA crossover system. A long entry triggers when the fast EMA (default 12) crosses above the slow EMA (default 26) while CHOP confirms a trending state. A short entry triggers on the opposite crossover under the same trending condition.

The emergency exit is the most distinctive feature: when CHOP rises above 61.8, all positions are closed immediately regardless of the EMA state. This Fibonacci-derived level represents a statistical extreme of choppiness where directional trades are unlikely to succeed. The strategy effectively goes flat during choppy markets and waits for the next trending phase.

This dual-filter approach dramatically reduces whipsaw losses. Standard EMA crossovers generate many false signals during sideways markets. By requiring CHOP confirmation, the strategy only trades during the market phases where trend-following has a genuine edge.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Choppiness Length | 14 | 5-50 | Lookback period for the Choppiness Index calculation |
| Fast EMA | 12 | 5-50 | Period for the fast exponential moving average |
| Slow EMA | 26 | 10-100 | Period for the slow exponential moving average |
| Chop Threshold | 50.0 | 30.0-70.0 | Maximum CHOP value to allow new trades; below = trending |

## Python Advantage

The strategy uses the `ta.chop()` function for vectorized Choppiness Index computation and combines it with EMA crossover detection in clean conditional logic.

```python
# Vectorized Choppiness Index — full history in one call
chop = ta.chop(high, low, close, chop_length)
fast = ta.ema(close, ema_fast)
slow = ta.ema(close, ema_slow)

# Current-bar trending check
is_trending = chop[-1] < chop_threshold

# Conditional entry: CHOP filter gates the EMA crossover
if is_trending and ta.crossover(fast, slow)[-1]:
    strategy.entry("Long", strategy.LONG)

# Emergency exit: close everything when market becomes choppy
if chop[-1] > 61.8:
    strategy.close_all()
```

The `strategy.close_all()` function provides a single-call emergency exit that closes every open position regardless of entry name or direction. This is particularly powerful for regime-change strategies where the market state invalidates all active trades simultaneously.

## When to Use

Best on instruments that alternate between clear trending and consolidation phases. Works well on daily timeframes for swing trading stocks, forex pairs, and futures. The strategy naturally avoids the most frustrating market condition for trend followers (sideways chop) while capturing the trending phases where EMA crossovers are profitable. Avoid on highly mean-reverting instruments that rarely produce sustained trends.

## Risk Management

The CHOP threshold is the primary risk control. Lowering it to 40 makes the trending requirement stricter, producing fewer but higher-quality trades. The 61.8 emergency exit provides catastrophic protection, but consider adding an ATR-based stop for individual trade risk management. During extended choppy periods, the strategy will be flat for long stretches, so ensure position sizing accounts for the reduced trade frequency.

## Combining with Other Indicators

- **ADX Trend**: Use ADX as a secondary trend confirmation alongside CHOP. Both indicators measuring trend strength provides stronger filtering than either alone.
- **ATR Trailing Stop**: Once the CHOP filter permits a trade, use ATR trailing stops for exit management rather than relying solely on the opposite EMA crossover.
- **BB Width Squeeze**: Identify squeeze conditions during choppy phases to anticipate when the next trending phase is about to begin.
