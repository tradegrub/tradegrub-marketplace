# Bollinger Band Bounce

The Bollinger Band Bounce is a mean-reversion strategy that trades price reactions at the upper and lower Bollinger Bands. Developed by John Bollinger in the 1980s, the bands represent standard deviation envelopes around a moving average. This strategy exploits the statistical tendency of price to revert toward the mean after touching or penetrating the outer bands, entering positions when price bounces off band extremes and optionally exiting at the middle basis line.

## Conceptual Diagram

```
Price
 │    · · · Upper Band (MA + 2σ) · · · ·
 │   ·  ╱╲  ·              · ╱╲ ·
 │  · ╱    ╲  ·           ·╱    ╲·
 │ · ╱      ╲  ·    ╱╲   ·╱      ╲
 │  ╱   ════ ╲══════╱═╲═╱════════ Basis
 │ ╱          ╲    ╱   ╳
 │╱         ·  ╲  ╱  · ╲·
 │        ·     ╲╱  ·    ╲·
 │       · · Lower Band · ·╲· · ·
 │                              ╲
 └──────────────────────────────── Time
   🔴 Cross below    🟢 Cross     🔴 Cross
   upper = short     above lower  below upper
        Exit at basis ──╳── Exit at basis
```

## How It Works

The strategy computes Bollinger Bands using a simple moving average and a standard deviation multiplier (default 2.0). The upper band sits at the basis plus two standard deviations, and the lower band at the basis minus two standard deviations. Statistically, approximately 95% of price action should fall within these bands under normal distribution assumptions.

When price crosses above the lower band from below, the strategy interprets this as a bounce off support and enters a long position. The logic is that price has been stretched to a statistical extreme and is now reverting toward the mean. Conversely, when price crosses below the upper band from above, the strategy enters a short position, expecting a reversion downward.

The optional exit-at-basis feature (enabled by default) closes positions when price reaches the middle band. Long positions close when price crosses below the basis, and short positions close when price crosses above the basis. This targets a conservative profit at the statistical center rather than holding for a full move to the opposite band.

This mean-reversion approach works best in range-bound markets where price oscillates between the bands. In strong trends, price can "walk the band," staying pressed against the upper or lower band for extended periods, which creates losses for the counter-trend entries.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| BB Length | 20 | 5-200 | Lookback period for the SMA basis and standard deviation calculation |
| BB Multiplier | 2.0 | 0.5-5.0 | Number of standard deviations for the upper and lower bands |
| Exit at Basis | true | true/false | Whether to close positions when price reaches the middle band |

## Python Advantage

The strategy uses the `ta.bb()` function to compute all three band components in a single vectorized call, with tuple unpacking for clean variable assignment.

```python
# Single call returns upper, basis, lower as numpy arrays
upper, basis, lower = ta.bb(close, length, mult)

# Crossover detection on dynamic band levels — not fixed thresholds
if ta.crossover(close, lower)[-1]:
    strategy.entry("Long", strategy.LONG)

if ta.crossunder(close, upper)[-1]:
    strategy.entry("Short", strategy.SHORT)

# Conditional exit logic controlled by boolean input parameter
if exit_at_basis:
    if ta.crossover(close, basis)[-1]:
        strategy.close("Short")
    if ta.crossunder(close, basis)[-1]:
        strategy.close("Long")
```

The `ta.bb()` tuple return eliminates the need to call separate functions for each band component. The `input.bool()` parameter creates a runtime-configurable toggle for the exit behavior, allowing traders to switch between basis exits and full-band-to-band holds without modifying code.

## When to Use

Best suited for range-bound and mean-reverting markets on 15-minute to daily timeframes. Works well with large-cap stocks in consolidation phases, forex pairs in established ranges, and index ETFs during low-volatility periods. Avoid during strong trending markets, breakout phases, or around major catalysts where price is likely to walk the band rather than bounce.

## Risk Management

The primary risk is trend continuation through the band. Place stops 1-2 ATR beyond the band that triggered the entry. When Exit at Basis is enabled, the strategy naturally limits holding time, reducing exposure to adverse moves. During trending markets, consider disabling the strategy entirely or adding a trend filter. The BB multiplier directly affects trade frequency: lower multipliers generate more signals but with less statistical edge per trade.

## Combining with Other Indicators

- **Choppiness Filter**: Use the Choppiness Index to confirm the market is range-bound before trusting band bounces, filtering out trending periods where bounces fail.
- **RSI Mean Reversion**: Add RSI confirmation to band touches. A lower band touch combined with RSI below 30 provides stronger mean-reversion confluence.
- **ADX Trend**: Use ADX below 20 as a pre-filter to ensure the market lacks directional momentum before trading bounces.
