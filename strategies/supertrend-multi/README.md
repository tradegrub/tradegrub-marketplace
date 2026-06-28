# Multi-Period Supertrend

The Multi-Period Supertrend strategy runs two Supertrend indicators with different speed settings and only enters trades when both agree on direction. The slow Supertrend acts as a trend filter (identifying the major move), while the fast Supertrend provides timing for entries and exits. This dual-confirmation approach dramatically reduces false signals compared to a single Supertrend system.

## Conceptual Diagram

```
Price
 |                  /\       /
 |        /\       /  \     /
 |       /  \     /    \   /
 |  /\  /    \   /      \ /
 | /  \/      \ /        V
 |/    ╱╱╱╱╱╱╱╱X╲╲╲╲╲╲╲╲╲    Fast ST
 |   ╱╱╱╱╱╱╱╱╱  ╲╲╲╲╲╲╲╲╲
 | ══════════════════════════  Slow ST
 |
 +──────────────────────────────── Time
   Both bullish:  Fast flips:  Both bullish:
      BUY           EXIT          BUY
   (fast+slow     (fast bear    (realign)
    above price)   = close)
```

## How It Works

Two Supertrend indicators are calculated: a fast version with shorter ATR length (10) and tighter multiplier (2.0), and a slow version with longer ATR length (20) and wider multiplier (3.0). Each produces a trailing support/resistance line that flips direction based on price action relative to ATR-based bands.

The entry logic requires both Supertrends to be bullish (price above both lines) for a long, or both bearish (price below both lines) for a short. This dual-confirmation ensures the trade aligns with the major trend (slow Supertrend) and has near-term momentum support (fast Supertrend).

Exits are controlled by the fast Supertrend alone. When the fast Supertrend flips bearish, long positions close immediately. This asymmetry -- slow filter for entry, fast trigger for exit -- keeps the strategy on the right side of major trends while responding quickly to momentum shifts.

The result is a system that stays out of choppy, directionless markets (where the two Supertrends disagree) and only participates in confirmed trends with clear momentum.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Fast Supertrend Length | 10 | 3 - 50 | ATR period for the fast (responsive) Supertrend |
| Fast Multiplier | 2.0 | 0.5 - 5.0 | ATR multiplier for the fast Supertrend bands |
| Slow Supertrend Length | 20 | 5 - 100 | ATR period for the slow (trend) Supertrend |
| Slow Multiplier | 3.0 | 1.0 - 8.0 | ATR multiplier for the slow Supertrend bands |

## Python Advantage

The strategy computes two independent Supertrend arrays and combines them with direct comparison operators:

```python
# Two Supertrend computations — independent array pipelines
st_fast = ta.supertrend(high, low, close, length1, mult1)
st_slow = ta.supertrend(high, low, close, length2, mult2)

# Direct scalar comparison via negative indexing
fast_bull = close[-1] > st_fast[-1]
slow_bull = close[-1] > st_slow[-1]

# Multi-condition entry — clean Python boolean logic
if fast_bull and slow_bull:
    strategy.entry("Long", strategy.LONG)
```

Python allows storing two separate Supertrend result arrays and comparing them independently against the close price. The boolean conditions combine naturally with `and` operators. Pine Script would require managing two separate sets of Supertrend variables and cannot store intermediate Supertrend arrays for later manipulation.

## When to Use

Multi-Period Supertrend is ideal for trending markets where you want to avoid the whipsaw that plagues single-Supertrend systems. It works well on crypto (strong momentum cycles), futures (clean trends), and trending stocks. Best on 1-hour to daily timeframes. The strategy will sit flat during ranging markets, which is a feature, not a bug.

## Risk Management

The fast Supertrend exit provides natural risk management, but the gap between the fast and slow Supertrend lines can widen during strong trends, meaning entries occur at a distance from the slow support. Size positions based on the distance to the fast Supertrend line as your initial risk reference. Consider reducing position size when the spread between the two Supertrend lines is unusually wide.

## Combining with Other Indicators

- **Squeeze Momentum** confirms that volatility expansion is supporting the dual-Supertrend alignment.
- **SuperTrend Pro** offers a single-line version with ATR trailing stops for comparison.
- **Trend Volatility Combo** adds volume confirmation to the Supertrend direction.
