# Cumulative Return Tracker

Running cumulative return tracker with drawdown overlay and benchmark comparison using numpy compounding calculations. This statistical analysis indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using statistical analysis techniques to produce actionable signals.

Built-in technical functions used: `sma`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include simple moving average, iterative computation. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Benchmark SMA Length | 50 | 10 - 200 | Controls benchmark sma length sensitivity (int) |

## Signals

- **Cumulative Return**: Primary visual output plotted as a continuous line on the chart
- **Drawdown %**: Primary visual output plotted as a continuous line on the chart
- **Breakeven** (100): Reference level for threshold-based decisions
- **Zero DD** (0): Reference level for threshold-based decisions
- **Background shading**: Highlights active signal zones based on deep_dd.tolist()

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
for i in range(1, n):
    cum_ret[i] = cum_ret[i-1] * (1 + daily_ret[i])

peak = np.zeros(n)
drawdown = np.zeros(n)
peak[0] = cum_ret[0]
for i in range(1, n):
    peak[i] = max(peak[i-1], cum_ret[i])
    drawdown[i] = (cum_ret[i] - peak[i]) / max(peak[i], 1e-10) * 100

sma_arr = np.array(ta.sma(close, bench_len), dtype=float)
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Quantify price behavior with statistical measures
- Identify when price deviates significantly from statistical norms
- Build probabilistic models for price movement expectations
- Detect regime changes through statistical anomalies

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
- **RSI or Stochastic**: Add a momentum oscillator as a confirmation filter. Signals that align with oversold or overbought momentum readings tend to produce larger moves.
