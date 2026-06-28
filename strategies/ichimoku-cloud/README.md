# Ichimoku Cloud

The Ichimoku Kinko Hyo ("one glance equilibrium chart") is a comprehensive technical analysis system developed by Japanese journalist Goichi Hosoda in the late 1930s, published in 1969 after three decades of refinement. Unlike most Western indicators that measure a single dimension of price action, Ichimoku provides a complete trading framework in a single view: trend direction, momentum, support/resistance levels, and entry signals. This strategy uses the cloud (Kumo) as a trend filter and the Tenkan-sen/Kijun-sen crossover as the entry trigger.

## Conceptual Diagram

```
Price
 |          ~~~:::::::::~~~          Senkou A ~~~
 |      ~~~:::::: CLOUD ::::~~~     Senkou B :::
 |  ~~~:::::::::::::::::::::::::~~~:::::::::::::
 |         ── Tenkan     ─ ─ Kijun
 |                ╱╲              ╱── Tenkan
 |          ╱╲  ╱    ╲     ╱╲  ╱
 |    ╱╲  ╱    ╲      ╲  ╱  ╲╱
 |  ╱  ╲╱      ╲      ╲╱
 | ╱    ╱╲       ╲    Kijun ─ ─ ─
 |╱    ╱  ╲       ╲         ╱╲
 |    ╱    ╲       ╲       ╱  ╲
 └──────────────────────────────── Time
    Price ABOVE cloud         Price ABOVE cloud
    + TK cross = 🟢 BUY      + TK cross = 🟢 BUY
              🔴 TK cross under = EXIT
```

## How It Works

The strategy combines two core Ichimoku components: the Kumo (cloud) for trend filtering and the Tenkan-sen/Kijun-sen crossover for entry timing. The Tenkan-sen is calculated as the midpoint of the highest high and lowest low over 9 periods, while the Kijun-sen uses 26 periods. The cloud is formed by Senkou Span A (average of Tenkan and Kijun, projected 26 periods forward) and Senkou Span B (midpoint of 52-period high/low, also projected forward).

A long entry is triggered when two conditions are met simultaneously: price must be trading above the cloud top (the higher of Senkou A and Senkou B), confirming a bullish trend, and the Tenkan-sen must cross above the Kijun-sen, providing the momentum trigger. The cloud top is computed using `np.maximum(senkou_a, senkou_b)` to dynamically select whichever span is higher at each bar.

The exit condition is straightforward: when the Tenkan-sen crosses below the Kijun-sen, the position is closed. This is a long-only strategy that avoids shorting, respecting the traditional Ichimoku philosophy that the cloud provides the most reliable signals in trending markets. The strategy does not enter when price is inside or below the cloud, filtering out choppy or bearish environments.

The visual output plots the full Ichimoku system: Tenkan-sen in blue, Kijun-sen in red, and the cloud filled between Senkou A (green) and Senkou B (maroon) with a semi-transparent green fill for easy identification.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Tenkan Period | 9 | 2 - 50 | Lookback for Tenkan-sen (fast equilibrium line) |
| Kijun Period | 26 | 5 - 100 | Lookback for Kijun-sen (slow equilibrium line) |
| Senkou B Period | 52 | 10 - 200 | Lookback for Senkou Span B (cloud boundary) |

## Python Advantage

The strategy leverages numpy's `np.maximum()` for element-wise cloud top computation across the entire price array in a single vectorized call, avoiding the bar-by-bar conditional logic required in Pine Script:

```python
# Vectorized cloud top — compares entire Senkou A and B arrays at once
cloud_top = np.maximum(senkou_a, senkou_b)
# Boolean condition evaluated across the full series in one operation
above_cloud = close[-1] > cloud_top[-1]
tk_cross = ta.crossover(tenkan, kijun)[-1]
# Combined entry: both conditions must be true on the current bar
long_cond = above_cloud and tk_cross
```

The `ta.ichimoku()` function returns all five Ichimoku lines in a single call with full-array computation, while Pine Script requires computing each component separately with redundant loops over the same data.

## When to Use

Ichimoku Cloud works best on daily and weekly timeframes in trending markets. It is particularly effective on forex pairs, equity indices, and large-cap stocks that exhibit sustained trends. Avoid using it on low-timeframe charts or highly range-bound instruments where the cloud becomes flat and generates excessive whipsaws.

## Risk Management

Place stop-loss orders below the Kijun-sen or below the cloud bottom, whichever is closer to price. The Kijun-sen acts as a natural trailing stop. Position sizing should account for the wider stops inherent in this system. Known limitation: Ichimoku signals lag significantly in fast-moving markets, and the 26-period projection means the cloud reflects past equilibrium, not current conditions.

## Combining with Other Indicators

- **Ichimoku RSI**: Add RSI filtering to avoid entries when momentum is exhausted, creating a more selective version of this strategy.
- **MACD Crossover**: Use MACD histogram direction to confirm the Tenkan/Kijun crossover momentum before entering.
- **Price Channel**: Validate breakout strength by confirming price is also breaking through the Donchian channel highs.
