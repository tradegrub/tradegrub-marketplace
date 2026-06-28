# Momentum Composite

The Momentum Composite combines three independent momentum oscillators, RSI, CCI, and Stochastic, into a single normalized score that reduces the noise and false signals inherent in any single momentum indicator. By averaging normalized readings from three mathematically distinct approaches to measuring momentum, this composite produces a more robust and reliable momentum gauge that smooths out the idiosyncratic weaknesses of each component.

## Conceptual Diagram

```text
 +100│
     │
  +50│┄┄┄┄┄┄┄┄┄╱╲┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ Overbought
     │        ╱  ╲          ╱╲
     │  ╱╲   ╱    ╲   ╱╲  ╱  ╲     Composite ───
     │ ╱  ╲ ╱      ╲ ╱  ╲╱    ╲    Signal - - -
   0 │╱────╳────────╳╱────╲─────╲──  Zero Line
     │    ╱ ╲      ╱      ╲     ╲
     │   ╱   ╲    ╱        ╲     ╲
     │  ╱     ╲  ╱          ╲     ╲
  -50│┄┄┄┄┄┄┄┄╲╱┄┄┄┄┄┄┄┄┄┄┄┄╲┄┄┄┄ Oversold
     │                        ╲
 -100│                         ╲
     └──────────────────────────────── Time
          Sell zone    Buy zone   Sell
```

## How It Works

The indicator first computes three independent momentum readings. RSI (default 14-period) measures the ratio of average gains to average losses. CCI (default 20-period) measures the deviation of price from its statistical mean. Stochastic (default 14-period) measures where the close sits within the recent high-low range.

Each oscillator is normalized to a common -1 to +1 scale. RSI is centered by subtracting 50 and dividing by 50, mapping its 0-100 range to -1 to +1. CCI is divided by 200 and clipped to -1/+1 using `np.clip`, preventing extreme CCI readings from dominating the composite. Stochastic is centered the same way as RSI: subtract 50, divide by 50.

The three normalized values are averaged and scaled to -100 to +100 to produce the composite score. A simple moving average (default 5-period) of the composite serves as a signal line. The composite crossing above or below the signal line provides trade timing, while the absolute level indicates momentum strength.

Readings above +50 indicate strong bullish momentum across all three components, highlighted with red background shading (overbought warning). Readings below -50 indicate strong bearish momentum, highlighted with green shading (oversold opportunity). The zero line separates net bullish from net bearish momentum.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| RSI Length | 14 | 5 - 50 | Lookback period for RSI calculation |
| CCI Length | 20 | 5 - 50 | Lookback period for CCI calculation |
| Stochastic Length | 14 | 5 - 50 | Lookback period for Stochastic calculation |
| Signal Length | 5 | 2 - 20 | SMA smoothing period for the signal line |

## Python Advantage

The normalization and composite computation leverage numpy's vectorized operations and clipping functions, processing all three oscillators across the entire price history simultaneously:

```python
import numpy as np

# Three independent oscillators computed as full arrays
rsi_val = ta.rsi(close, rsi_len)
cci_val = ta.cci(close, cci_len)
stoch_val = ta.stoch(high, low, close, stoch_len)

# Vectorized normalization to common -1 to +1 scale
rsi_norm = (rsi_val - 50) / 50
cci_norm = np.clip(cci_val / 200, -1, 1)  # Clip prevents CCI extremes
stoch_norm = (stoch_val - 50) / 50

# Composite: average and scale in one vectorized expression
composite = (rsi_norm + cci_norm + stoch_norm) / 3 * 100
signal = ta.sma(composite, signal_len)
```

The `np.clip` function bounds the CCI normalization across all bars in a single call, preventing outlier CCI values from overwhelming the composite. In Pine Script, you would need `math.min(math.max(...))` evaluated bar-by-bar. The entire normalization pipeline is pure array arithmetic, and extending it to include additional oscillators (Williams %R, MFI) requires only adding one normalization line and adjusting the divisor.

## When to Use

The Momentum Composite works on all timeframes and asset classes. It is most effective on daily and 4-hour charts for swing trading. Use it for momentum-based entries and exits, or as a confirmation filter for trend-following signals. Divergences between the composite and price (price making new highs while composite is declining) are particularly reliable reversal signals because they reflect agreement across three independent momentum measures.

## Risk Management

Overbought readings (+50 and above) do not automatically mean sell; in strong trends, momentum can stay overbought for extended periods. Use overbought/oversold levels as warnings to tighten stops rather than as outright reversal signals. The signal line crossover provides better timing than the absolute level. During low-volatility environments, the composite may oscillate narrowly around zero, producing unreliable signals.

## Combining with Other Indicators

- **Market Regime**: Use the regime detector to determine whether to treat composite extremes as trend continuation (trending regime) or reversal (ranging regime) signals.
- **Correlation Indicator**: When the Momentum Composite diverges from price and correlation is also declining, the double divergence strengthens the reversal case.
- **Fibonacci Bands**: Enter at Fibonacci support levels when the composite is oversold, combining price-level and momentum confirmation.
