# Detrended Rhythm Oscillator

Detrends price with SMA removal and finds dominant cycle via autocorrelation, plotting the rhythmic oscillation with peak and trough markers. This cycle analysis indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using cycle analysis techniques to produce actionable signals.

Built-in technical functions used: `sma`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include simple moving average, iterative computation, standard deviation analysis, mean computation. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Detrend Length | 50 | 10 - 200 | Controls detrend length sensitivity (int) |
| Max Cycle | 40 | 5 - 100 | Controls max cycle sensitivity (int) |

## Signals

- **Rhythm Oscillator**: Primary visual output plotted as a continuous line on the chart
- **Detrended Price**: Primary visual output plotted as a continuous line on the chart
- **Cycle Peak**: Discrete signal marker displayed at key points
- **Cycle Trough**: Discrete signal marker displayed at key points
- **Zero** (0): Reference level for threshold-based decisions
- **Upper** (1.5): Reference level for threshold-based decisions
- **Lower** (-1.5): Reference level for threshold-based decisions

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
cl = np.array(close, dtype=float)
n = len(cl)

sma_arr = np.array(ta.sma(close, detrend_length), dtype=float)
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
