# Multi-Oscillator Consensus

A voting-based momentum strategy that requires agreement from multiple oscillators before generating trade signals. Rooted in the principle that no single oscillator is reliable on its own, this approach combines RSI, CCI, and Stochastic into a consensus scoring system. When two or three oscillators agree on direction, the signal carries significantly more weight than any individual reading, filtering out the false signals that plague single-indicator strategies.

## Conceptual Diagram

```
  100 ┬─────────────────────────────────────────────
      │          ╱╲              RSI (blue)
      │    ╱╲   ╱  ╲   ╱╲       Stoch %K (purple)
      │   ╱  ╲ ╱    ╲ ╱  ╲      CCI scaled (orange)
   50 ┼──╱────X──────X────╲─── Midline ────────────
      │ ╱    ╱ ╲    ╱ ╲    ╲
      │╱    ╱   ╲  ╱   ╲    ╲
      │    ╱     ╲╱     ╲    ╲
    0 ┴─────────────────────────────────────────────
      │    │              │
      │ All 3 above 50   │ All 3 below 50
      │ Score: 3/3        │ Score: 3/3
      │ 🟢 BUY            │ 🔴 SELL
      │ (new consensus)   │ (new consensus)
```

## How It Works

The strategy calculates three independent oscillators on each bar: the Relative Strength Index (RSI), the Commodity Channel Index (CCI), and the Stochastic %K (smoothed). Each oscillator is evaluated against its own midline to determine directional bias. RSI above 50 is bullish, CCI above 0 is bullish, and Stochastic %K above 50 is bullish. The inverse applies for bearish readings.

Each bullish or bearish reading contributes one point to a consensus score ranging from 0 to 3. The `consensus` parameter sets the minimum agreement required, either 2-of-3 or 3-of-3. A higher consensus requirement produces fewer but higher-conviction signals.

Signals fire only on transitions. The strategy tracks whether the previous bar already met the consensus threshold, and only enters a trade when the consensus is newly achieved. This prevents repeated entries during sustained trends and focuses on the initial momentum shift.

Entries are directional: a new bullish consensus triggers a long entry, while a new bearish consensus triggers a short entry. There are no fixed take-profit or stop-loss levels built in, making this strategy best used as a signal generator paired with your own exit rules or another strategy's risk management.

The CCI is scaled (divided by 4 and shifted by 50) for plotting purposes so all three oscillators display on the same 0-100 scale. This scaling is cosmetic only and does not affect the trading logic.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| RSI Length | 14 | 2 - 50 | Lookback period for RSI calculation |
| CCI Length | 20 | 5 - 50 | Lookback period for CCI calculation |
| Stochastic Length | 14 | 2 - 50 | Lookback period for Stochastic %K |
| Stochastic Smoothing | 3 | 1 - 10 | SMA smoothing applied to raw %K |
| Min Consensus | 2 | 2 - 3 | Minimum number of oscillators that must agree |

## Python Advantage

Pine Script cannot natively cast boolean arrays to integers and sum them in a vectorized operation. In Python with NumPy, the consensus scoring is a single vectorized expression across the entire dataset:

```python
bull_score = rsi_bull.astype(int) + cci_bull.astype(int) + stoch_bull.astype(int)
bear_score = rsi_bear.astype(int) + cci_bear.astype(int) + stoch_bear.astype(int)

long_cond = bull_score >= consensus
short_cond = bear_score >= consensus
```

This approach processes thousands of bars instantly and makes it trivial to add a fourth or fifth oscillator to the voting system without restructuring the logic.

## When to Use

Best suited for swing trading on daily or 4-hour charts across equities, ETFs, and forex pairs. The multi-oscillator approach shines in choppy or transitioning markets where a single oscillator would whipsaw. Avoid using during extremely low-volatility consolidation periods where all oscillators cluster near their midlines.

## Risk Management

Since this strategy does not include built-in stop-loss or take-profit levels, you should pair it with ATR-based stops or a fixed percentage risk per trade. Position size according to the distance between entry and your chosen stop level. A known limitation is that in strong trending markets, bearish consensus signals can fire prematurely against the trend. Consider adding a trend filter (such as a 50-period SMA direction check) to avoid counter-trend entries.

## Combining with Other Indicators

- **ATR Trailing Stop**: Use the ATR-based trailing stop strategy to manage exits after the multi-oscillator generates an entry signal.
- **ADX Trend Filter**: Layer the ADX trend strategy on top to suppress signals when the market lacks directional strength (ADX below 20).
- **Bollinger Bands**: Use Bollinger Band width to confirm that volatility is present before acting on consensus signals.
