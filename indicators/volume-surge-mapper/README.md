# Volume Surge Mapper

Detects and maps volume surges using scipy statistical z-score analysis with intensity classification and directional bias. This volume-based indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using volume-based techniques to produce actionable signals.

Core techniques include simple moving average, iterative computation, standard deviation analysis, mean computation. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

Float parameters fine-tune sensitivity and scaling factors. Small adjustments to these values can significantly change signal frequency and quality, so test changes on historical data before applying to live trading.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback Length | 20 | 10 - 100 | Controls lookback length sensitivity (int) |
| Moderate Threshold (z | 1.5 |  | Controls moderate threshold (z sensitivity (float) |
| Strong Threshold (z | 2.5 |  | Controls strong threshold (z sensitivity (float) |

## Signals

- **Volume Z-Score**: Primary visual output plotted as a continuous line on the chart
- **Volume Ratio**: Primary visual output plotted as a continuous line on the chart
- **Strong Surge**: Discrete signal marker displayed at key points
- **Moderate** (moderate_z): Reference level for threshold-based decisions
- **Strong** (strong_z): Reference level for threshold-based decisions
- **Zero** (0): Reference level for threshold-based decisions
- **Background shading**: Highlights active signal zones based on bull_surge
- **Background shading**: Highlights active signal zones based on bear_surge

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
vol = np.array(volume, dtype=float)
cl = np.array(close, dtype=float)
op = np.array(open, dtype=float)
n = len(cl)

z_score = np.zeros(n)
vol_ratio = np.zeros(n)

for i in range(length, n):
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Confirm price moves with volume participation
- Identify accumulation and distribution phases
- Detect institutional activity through volume anomalies
- Filter false breakouts that lack volume confirmation

Works best on daily and intraday charts for liquid instruments. Shorter parameter values suit scalping and day trading while longer values work for swing and position trading.

## Risk Management

No indicator is predictive on its own. Always define risk before entering a trade:

- Set stop-losses based on ATR or recent swing points, not arbitrary percentages
- Size positions so that a stop-loss hit risks no more than 1-2% of account equity
- Avoid adding to losing positions based solely on indicator readings
- Backtest parameter combinations on out-of-sample data before live trading

## Combining with Other Indicators

- **Moving Average Ribbon**: Use the Moving Average Ribbon to confirm the overall trend direction before acting on this indicator's signals. Trading in the direction of the ribbon produces higher win rates.
- **RSI or Stochastic**: Add a momentum oscillator as a confirmation filter. Signals that align with oversold or overbought momentum readings tend to produce larger moves.
- **ATR-Based Stops**: Use ATR to set stop-losses that respect current volatility. Tighter stops in low-volatility environments and wider stops during volatile periods improve the reward-to-risk ratio.
