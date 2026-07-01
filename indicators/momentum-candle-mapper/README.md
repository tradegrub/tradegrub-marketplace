# Momentum Candle Mapper

Reinterprets momentum values as candlestick-style visualization with optional smoothing for clearer trend identification using numpy. This momentum indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using momentum techniques to produce actionable signals.

Built-in technical functions used: `sma`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include simple moving average, iterative computation, extremum detection, high-low range analysis. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Momentum Length | 10 | 3 - 30 | Controls momentum length sensitivity (int) |
| Smoothing | 3 | 1 - 10 | Controls smoothing sensitivity (int) |

## Signals

- **Momentum Close**: Primary visual output plotted as a continuous line on the chart
- **Momentum Open**: Primary visual output plotted as a continuous line on the chart
- **Zero** (0): Reference level for threshold-based decisions

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
for i in range(1, n):
        ha_op[i] = (ha_op[i-1] + ha_cl[i-1]) / 2
    ha_hi = np.maximum(np.maximum(mom_hi, ha_op), ha_cl)
    ha_lo = np.minimum(np.minimum(mom_lo, ha_op), ha_cl)
    mom_cl = ha_cl
    mom_op = ha_op
    mom_hi = ha_hi
    mom_lo = ha_lo

if smooth > 1:
    mom_cl = np.array(ta.sma(mom_cl.tolist(), smooth), dtype=float)
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
