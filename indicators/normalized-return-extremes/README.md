# Normalized Return Extremes

Volatility-normalized returns analysis measuring statistical extremes and regime changes using scipy z-score and percentile calculations. This statistical analysis indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using statistical analysis techniques to produce actionable signals.

Built-in technical functions used: `atr`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include ATR, iterative computation, standard deviation analysis, mean computation. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

Float parameters fine-tune sensitivity and scaling factors. Small adjustments to these values can significantly change signal frequency and quality, so test changes on historical data before applying to live trading.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Return Period | 5 | 1 - 20 | Controls return period sensitivity (int) |
| Normalization Window | 60 | 30 - 200 | Controls normalization window sensitivity (int) |
| Extreme Threshold (z | 2.0 |  | Controls extreme threshold (z sensitivity (float) |

## Signals

- **Normalized Z-Score**: Primary visual output plotted as a continuous line on the chart
- **Volatility Regime**: Primary visual output plotted as a continuous line on the chart
- **Upper Extreme** (extreme_z): Reference level for threshold-based decisions
- **Lower Extreme** (-extreme_z): Reference level for threshold-based decisions
- **Zero** (0): Reference level for threshold-based decisions
- **Regime Baseline** (1): Reference level for threshold-based decisions
- **Background shading**: Highlights active signal zones based on extreme_up.tolist()
- **Background shading**: Highlights active signal zones based on extreme_down.tolist()

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
cl = np.array(close, dtype=float)
n = len(cl)

returns = np.zeros(n)
for i in range(ret_len, n):
    returns[i] = (cl[i] - cl[i-ret_len]) / max(cl[i-ret_len], 1e-10) * 100

atr_arr = np.array(ta.atr(high, low, close, 14), dtype=float)
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
