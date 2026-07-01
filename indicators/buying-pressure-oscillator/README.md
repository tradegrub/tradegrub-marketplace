# Buying Pressure Oscillator

Short-term oscillator measuring buying and selling pressure cycles over configurable time intervals for momentum analysis using numpy cycle detection. This momentum indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using momentum techniques to produce actionable signals.

Built-in technical functions used: `sma`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include simple moving average, iterative computation, conditional array operations, high-low range analysis. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Wave Length | 14 | 5 - 40 | Controls wave length sensitivity (int) |
| Smoothing | 3 | 1 - 10 | Controls smoothing sensitivity (int) |

## Signals

- **Buying Pressure**: Primary visual output plotted as a continuous line on the chart
- **Overbought** (40): Reference level for threshold-based decisions
- **Oversold** (-40): Reference level for threshold-based decisions
- **Zero** (0): Reference level for threshold-based decisions
- **Background shading**: Highlights active signal zones based on ob.tolist()
- **Background shading**: Highlights active signal zones based on os_zone.tolist()

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
for i in range(length, n):
    buy_sum[i] = np.sum(buy_ratio[i-length+1:i+1])
    sell_sum[i] = np.sum(sell_ratio[i-length+1:i+1])

wave = np.zeros(n)
for i in range(length, n):
    total = buy_sum[i] + sell_sum[i]
    if total > 0:
        wave[i] = (buy_sum[i] - sell_sum[i]) / total * 100

smoothed = np.array(ta.sma(wave.tolist(), smooth), dtype=float)
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Detect acceleration or deceleration in price movement
- Identify divergences between price and momentum for reversal signals
- Confirm breakout strength before committing capital
- Time exits when momentum begins to fade

Works best on daily and intraday charts for liquid instruments. Shorter parameter values suit scalping and day trading while longer values work for swing and position trading.

## Risk Management

No indicator is predictive on its own. Always define risk before entering a trade:

- Set stop-losses based on ATR or recent swing points, not arbitrary percentages
- Size positions so that a stop-loss hit risks no more than 1-2% of account equity
- Avoid adding to losing positions based solely on indicator readings
- Backtest parameter combinations on out-of-sample data before live trading

## Combining with Other Indicators

- **Moving Average Ribbon**: Use the Moving Average Ribbon to confirm the overall trend direction before acting on this indicator's signals. Trading in the direction of the ribbon produces higher win rates.
- **Volume Profile POC**: When this indicator's signal aligns with a high-volume node from the Volume Profile, the confluence creates a stronger setup with better follow-through.
- **ATR-Based Stops**: Use ATR to set stop-losses that respect current volatility. Tighter stops in low-volatility environments and wider stops during volatile periods improve the reward-to-risk ratio.
