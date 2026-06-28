# Squeeze Momentum

The Squeeze Momentum strategy detects periods when Bollinger Bands contract inside Keltner Channels, signaling an impending volatility expansion. Originally conceptualized by John Carter in his book "Mastering the Trade," the squeeze identifies compressed markets that are coiling for a directional breakout. When the squeeze releases and momentum is positive, the strategy enters long, riding the explosive move that typically follows low-volatility consolidation.

## Conceptual Diagram

```
Price
 |              Keltner Channel (wider)
 |    ┊  ┊  ┊ ╱╲         ╱
 |    ┊BB┊  ┊╱  ╲       ╱
 |    ┊in┊  ╱    ╲     ╱
 |    ┊KC┊ ╱      ╲   ╱
 |    ┊  ┊╱        ╲ ╱
 +────────┤──────────╳───────── Time
          |SQUEEZE   |RELEASE
          |  OFF     |
Momentum
 |                   /\
 |                  /  \
 0 ─────────────── /────\──── Zero
 |   /\   /\     /      \
 |  /  \_/  \   /
 +──────────────────────────── Time
    (squeeze)    BUY    EXIT
                 (mom>0) (mom<0)
```

## How It Works

The strategy calculates both Bollinger Bands (based on standard deviation) and Keltner Channels (based on ATR) over the same lookback period. A squeeze is detected when the Bollinger Bands fall entirely within the Keltner Channels, meaning volatility has contracted below normal levels.

The critical signal occurs when the squeeze releases: the Bollinger Bands expand back outside the Keltner Channels. At this moment, the strategy checks the momentum value (derived from the `ta.squeeze` function). If momentum is positive at the release point, a long entry fires. This combination ensures the strategy only enters when volatility is expanding in a bullish direction.

Exits trigger when momentum crosses below zero, indicating the directional impulse has faded. The background is highlighted red during active squeeze periods, providing a visual "coiling" warning on the chart.

The squeeze is timeframe-agnostic: it measures relative volatility compression regardless of whether you are on a 5-minute or daily chart, making it one of the most versatile momentum strategies available.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| BB Length | 20 | 5 - 50 | Bollinger Bands lookback period |
| BB Multiplier | 2.0 | 0.5 - 4.0 | Standard deviation multiplier for Bollinger Bands |
| KC Length | 20 | 5 - 50 | Keltner Channel lookback period |
| KC Multiplier | 1.5 | 0.5 - 4.0 | ATR multiplier for Keltner Channel width |

## Python Advantage

The `ta.squeeze` function returns both the squeeze state and momentum as full arrays, enabling clean release detection via array indexing:

```python
squeeze_on, momentum = ta.squeeze(close, high, low, close,
                                   bb_length, bb_mult, kc_length, kc_mult)

# Squeeze release detection — compare consecutive bars via negative indexing
squeeze_off = squeeze_on[-2] and not squeeze_on[-1]

# Directional entry only on release with positive momentum
if squeeze_off and momentum[-1] > 0:
    strategy.entry("Long", strategy.LONG)
```

The tuple unpacking of `(squeeze_on, momentum)` from a single function call is a Python pattern that Pine Script cannot replicate. Pine requires separate variable assignments from the same function call using `plot` indices. The `squeeze_on[-2] and not squeeze_on[-1]` transition detection is natural array logic.

## When to Use

Squeeze Momentum works on all timeframes and instruments. It is especially effective on volatile markets like crypto and futures where consolidation-to-expansion cycles are pronounced. The strategy excels on 15-minute to daily charts. It is a long-only setup in this implementation; consider pairing with a short-side strategy for complete coverage.

## Risk Management

The squeeze release can occasionally fire on low-conviction moves. Without a built-in stop, a failed breakout can result in extended drawdowns while waiting for momentum to cross zero. Consider adding an ATR-based stop or a time-based exit for trades that fail to develop momentum within a few bars of entry.

## Combining with Other Indicators

- **Range Breakout** confirms the squeeze release aligns with a Donchian channel breakout.
- **Volatility Breakout** provides a BBW-percentile alternative to the Keltner-based squeeze detection.
- **ADX Trend + RSI Momentum Filter** validates that the post-squeeze move has genuine trend strength.
