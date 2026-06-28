# Fibonacci Retracement Bands

Fibonacci Retracement Bands dynamically project key Fibonacci levels (23.6%, 38.2%, 50%, 61.8%, 78.6%) across the rolling high-low range of price action. Rooted in the mathematical properties of the Fibonacci sequence discovered by Leonardo of Pisa in the 13th century, these ratios appear frequently in natural systems and have been adopted by traders since the 1930s as reliable zones where price tends to find support or resistance during pullbacks within trends.

## Conceptual Diagram

```text
Price
 │  _______________________________________ Range High (100%)
 │  . . . . . . . . . . . . . . . . . . .  78.6%
 │
 │  - - - - - - - - - - - - - - - - - - -  61.8%  Resistance
 │               ╱╲      ╱╲
 │  ════════════╱══╲════╱══╲══════════════  50.0%  Midpoint
 │             ╱    ╲  ╱    ╲
 │  - - - - -╱- - - ╲╱- - - ╲- - - - - -  38.2%  Support
 │          ╱        ·        ╲
 │  . . . .╱. . . . . . . . . ╲. . . . .  23.6%
 │        ╱                     ╲
 │  _______________________________________ Range Low (0%)
 └──────────────────────────────────────── Time
          Pullback bounces off 38.2%
             "Golden Zone" filled
```

## How It Works

The indicator first identifies the highest high and lowest low over the configurable lookback period (default 50 bars) to establish the current price range. This range updates dynamically as new extremes form, so the Fibonacci levels shift with evolving market structure rather than being anchored to a static swing.

Five Fibonacci retracement levels are calculated within this range. Each level represents a percentage of the range added to the low: 23.6% sits just above the range low, 50% marks the exact midpoint, and 78.6% sits near the range high. These levels act as probabilistic support and resistance zones derived from the golden ratio (1.618) and its inverses.

The 61.8% and 38.2% levels are the most significant in practice. During uptrends, pullbacks that hold at the 38.2% retracement are considered shallow and bullish, indicating strong buying interest. Pullbacks to 61.8% are deeper corrections that still maintain the trend structure. A break below the 23.6% level typically signals trend failure.

An optional fill between the 38.2% and 61.8% levels highlights the "golden zone" where the highest-probability reversals occur. Price spending time within this zone during a pullback often precedes a continuation move in the direction of the larger trend.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback Length | 50 | 10 - 200 | Number of bars to determine the high-low range |
| Show Fill | true | Boolean | Fill the area between the 38.2% and 61.8% levels |

## Python Advantage

The entire Fibonacci level computation is expressed as simple arithmetic on numpy arrays, with each level calculated in a single vectorized operation across all bars simultaneously:

```python
# Vectorized range and Fibonacci level computation
hi = ta.highest(high, length)
lo = ta.lowest(low, length)
rng = hi - lo

# All five levels computed as scalar-multiplied array operations
fib_236 = lo + rng * 0.236
fib_382 = lo + rng * 0.382
fib_500 = lo + rng * 0.500
fib_618 = lo + rng * 0.618
fib_786 = lo + rng * 0.786
```

Python's ability to broadcast scalar multiplication across entire arrays means all five Fibonacci levels are computed simultaneously for every bar in the dataset. Adding custom ratios (e.g., `fib_707 = lo + rng * 0.707`) is a single line. You could also compute inter-level distances as arrays (`zone_width = fib_618 - fib_382`) for adaptive stop placement, or use `np.where(close < fib_382, "support", "above")` for regime classification.

## When to Use

Fibonacci Bands work best during trending markets with clear pullbacks. They are most effective on daily and weekly charts for swing trading, though they also perform well on 1-hour and 4-hour charts for active traders. They apply to any liquid instrument including equities, forex, futures, and crypto. Avoid using them during extended sideways consolidation where the range contracts to meaningless levels.

## Risk Management

Place stop-losses just beyond the next Fibonacci level below your entry. For example, if entering long at the 38.2% retracement, set stops below the 23.6% level. The distance between Fibonacci levels provides natural risk units for position sizing. Be aware that during strong trends, price may not retrace to any Fibonacci level at all, so do not force entries at levels that price has clearly bypassed.

## Combining with Other Indicators

- **Volume Profile POC**: When the Point of Control aligns with a Fibonacci level, the confluence creates a particularly strong support or resistance zone.
- **VWAP StdDev Bands**: Fibonacci levels near VWAP bands provide double confirmation of mean-reversion zones.
- **Trend Strength**: Use the Trend Strength score to determine whether a Fibonacci pullback is occurring within a strong trend (high score) or a weakening one (declining score).
