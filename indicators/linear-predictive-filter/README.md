# Linear Predictive Filter

Linear Predictive Coding via Yule-Walker equations to extract dominant cycles and predict the next price value. This cycle analysis indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using cycle analysis techniques to produce actionable signals.

Core techniques include convolution, simple moving average, iterative computation, standard deviation analysis. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| LPC Order | 10 | 4 - 30 | Controls lpc order sensitivity (int) |
| Lookback | 100 | 50 - 300 | Controls lookback sensitivity (int) |

## Signals

- **LPC Predicted Price**: Primary visual output plotted as a continuous line on the chart
- **Dominant Cycle Length**: Primary visual output plotted as a continuous line on the chart
- **Zero** (0): Reference level for threshold-based decisions

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
src = np.array(close, dtype=float)
n = len(src)

predicted = np.full(n, np.nan)
cycle_length = np.full(n, np.nan)

for i in range(lookback, n):
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Identify dominant price cycles and their current phase
- Time entries at cycle troughs and exits at cycle peaks
- Detect when cycles are in phase for stronger signals
- Filter signals that align with the dominant cycle direction

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
