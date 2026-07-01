# Trend Regime Classifier

General-purpose trend capture and bias filter using statistical and digital signal processing methods for regime detection and trend classification. This trend-following indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using trend-following techniques to produce actionable signals.

Built-in technical functions used: `sma`. These provide the foundation for the indicator's calculations, computed efficiently across the full price history in a single pass.

Core techniques include simple moving average, iterative computation, standard deviation analysis, mean computation. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Fast Period | 10 | 3 - 30 | Controls fast period sensitivity (int) |
| Slow Period | 40 | 20 - 100 | Controls slow period sensitivity (int) |
| Regime Window | 30 | 15 - 80 | Controls regime window sensitivity (int) |

## Signals

- **Trend Score**: Primary visual output plotted as a continuous line on the chart
- **Regime**: Primary visual output plotted as a continuous line on the chart
- **Neutral** (0): Reference level for threshold-based decisions
- **Background shading**: Highlights active signal zones based on strong_up.tolist()
- **Background shading**: Highlights active signal zones based on strong_down.tolist()

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
fast_ma = lfilter(b_fast, 1, cl)
slow_ma = lfilter(b_slow, 1, cl)

trend_score = np.zeros(n)
for i in range(slow_len, n):
    fast_slope = (fast_ma[i] - fast_ma[max(0, i-5)]) / max(abs(fast_ma[max(0, i-5)]), 1e-10)
    slow_slope = (slow_ma[i] - slow_ma[max(0, i-5)]) / max(abs(slow_ma[max(0, i-5)]), 1e-10)
    spread = (fast_ma[i] - slow_ma[i]) / max(abs(slow_ma[i]), 1e-10)
    trend_score[i] = (fast_slope * 500 + slow_slope * 300 + spread * 200) / 3

smoothed = np.array(ta.sma(trend_score.tolist(), 5), dtype=float)
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
