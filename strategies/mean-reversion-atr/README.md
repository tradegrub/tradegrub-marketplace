# ATR Mean Reversion

This strategy builds dynamic bands around a simple moving average using the Average True Range (ATR) as the volatility measure. When price stretches beyond a configurable ATR multiple from the SMA, it is considered overextended and likely to revert back toward the mean. The strategy enters when price crosses back inside the band from an extreme and exits at the SMA itself, capturing the reversion move. Unlike Bollinger Bands (which use standard deviation), ATR-based bands adapt specifically to candlestick range volatility, making them responsive to genuine price movement.

## Conceptual Diagram

```
Price
 |  - - - Upper ATR Band (SMA + 2.5 * ATR) - - -
 |         /\
 |        /  \             /\
 |       /    \   /\      /  \
 |      /      \ /  \    /    \
 |=== SMA ======X====\==/===== SMA (target) ===
 |     \        /\    \/      /
 |      \      /  \    \     /
 |       \    /    \    \   /
 |        \  /      \    \ /
 |  - - - Lower ATR Band (SMA - 2.5 * ATR) - - -
 |         ^              ^
 |    Price crosses   Price crosses
 |    above lower     below upper
 +-------------------------------------------- Time
       BUY LONG         SELL SHORT
      (exit at SMA)    (exit at SMA)
```

## How It Works

The strategy computes a simple moving average (default 50 periods) and the Average True Range (default 14 periods). The upper band is SMA + ATR * multiplier, and the lower band is SMA - ATR * multiplier. The default multiplier of 2.5 creates bands wide enough to capture significant overextensions while filtering out normal price noise.

Long entries trigger when price crosses above the lower band from below, detected by `ta.crossover(close, lower_band)`. This means price had been below the lower ATR extreme and is now reversing upward, starting the reversion toward the SMA.

Short entries trigger when price crosses below the upper band from above, detected by `ta.crossunder(close, upper_band)`. This means price had been above the upper ATR extreme and is now reversing downward.

Exits are at the SMA itself: longs close when price crosses below the SMA, and shorts close when price crosses above it. The SMA acts as the equilibrium target for the mean reversion trade. This provides a clean, symmetric system where entries are at band extremes and exits are at the midline.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| SMA Length | 50 | 10-200 | Moving average period for the center line |
| ATR Length | 14 | 5-50 | ATR calculation period |
| ATR Multiplier | 2.5 | 1.0-5.0 | Band width in ATR units from SMA |

## Python Advantage

The band construction uses direct numpy array arithmetic, computing the entire band history in two operations:

```python
sma = ta.sma(close, sma_length)
atr = ta.atr(high, low, close, atr_length)

# Vectorized band computation -- element-wise across all bars
upper_band = sma + atr * atr_mult
lower_band = sma - atr * atr_mult

# Crossover detection on computed arrays
if ta.crossover(close, lower_band)[-1]:
    strategy.entry("Long", strategy.LONG)
if ta.crossunder(close, upper_band)[-1]:
    strategy.entry("Short", strategy.SHORT)
```

The expressions `sma + atr * atr_mult` and `sma - atr * atr_mult` leverage numpy broadcasting to multiply and add across the entire time series in a single operation. Each element of the `atr` array is multiplied by the scalar `atr_mult`, then added to the corresponding `sma` element. Pine Script computes this bar-by-bar. Python's array arithmetic also makes it trivial to compute derived statistics like band width percentile, adaptive multipliers, or band slope for trend detection.

## When to Use

ATR mean reversion works best in range-bound to moderately trending markets on daily and 4-hour timeframes. It is effective for large-cap equities, index ETFs, and forex pairs that oscillate around a central tendency. The strategy struggles during strong momentum breakouts where price pushes beyond the bands and continues trending. Higher ATR multipliers (3.0+) reduce trade frequency but increase win rate by targeting only extreme deviations.

## Risk Management

Stop-losses should be placed at a fixed distance beyond the band (e.g., 1x ATR beyond the band at entry), since a continued move away from the mean suggests a regime change rather than reversion. The risk per trade equals the distance from the band to the stop, and the reward equals the distance from the band to the SMA. With a 2.5x multiplier, this typically provides a favorable risk-reward ratio. Reduce position size when ATR is elevated, as the wider bands mean larger potential drawdowns.

## Combining with Other Indicators

- **Momentum Divergence**: Check for RSI divergence at the ATR band touch to confirm that price momentum is indeed weakening before entering a reversion trade.
- **Multi-Oscillator Consensus**: Use consensus scoring from RSI, CCI, and Stochastic to validate oversold/overbought conditions at the bands.
- **MA Crossover**: Use a moving average crossover to determine the dominant trend direction and only take ATR reversion trades aligned with that trend.
