# Trend Timing Oscillator

Enhanced Aroon-based trend timing with maturity scoring that rates trend age and strength using numpy statistical analysis. This trend-following indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using trend-following techniques to produce actionable signals.

Core techniques include iterative computation, high-low range analysis. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Aroon Length | 25 | 10 - 100 | Controls aroon length sensitivity (int) |
| Maturity Window | 10 | 3 - 30 | Controls maturity window sensitivity (int) |

## Signals

- **Aroon Oscillator**: Primary visual output plotted as a continuous line on the chart
- **Trend Maturity**: Primary visual output plotted as a continuous line on the chart
- **Strong Up** (50): Reference level for threshold-based decisions
- **Strong Down** (-50): Reference level for threshold-based decisions
- **Zero** (0): Reference level for threshold-based decisions
- **Background shading**: Highlights active signal zones based on strong_up.tolist()
- **Background shading**: Highlights active signal zones based on strong_down.tolist()

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
hi = np.array(high, dtype=float)
lo = np.array(low, dtype=float)
n = len(hi)

aroon_up = np.zeros(n)
aroon_down = np.zeros(n)
for i in range(length, n):
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Identify the dominant trend direction before entering positions
- Filter out counter-trend signals from other indicators
- Time entries during trend pullbacks to moving average or trend line support
- Set trailing stops that follow the trend progression

Works best on daily and intraday charts for liquid instruments. Shorter parameter values suit scalping and day trading while longer values work for swing and position trading.

## Risk Management

No indicator is predictive on its own. Always define risk before entering a trade:

- Set stop-losses based on ATR or recent swing points, not arbitrary percentages
- Size positions so that a stop-loss hit risks no more than 1-2% of account equity
- Avoid adding to losing positions based solely on indicator readings
- Backtest parameter combinations on out-of-sample data before live trading

## Combining with Other Indicators

- **Volume Profile POC**: When this indicator's signal aligns with a high-volume node from the Volume Profile, the confluence creates a stronger setup with better follow-through.
- **RSI or Stochastic**: Add a momentum oscillator as a confirmation filter. Signals that align with oversold or overbought momentum readings tend to produce larger moves.
- **ATR-Based Stops**: Use ATR to set stop-losses that respect current volatility. Tighter stops in low-volatility environments and wider stops during volatile periods improve the reward-to-risk ratio.
