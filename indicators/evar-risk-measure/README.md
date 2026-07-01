# Entropy Risk Measure

Entropy-adjusted Value at Risk using Cornish-Fisher expansion with skewness and kurtosis correction, plus suggested position sizing. This risk management indicator provides quantitative signals that can be applied to any liquid market across all timeframes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The indicator analyzes price data using risk management techniques to produce actionable signals.

Core techniques include logarithmic transformation, iterative computation, conditional array operations, standard deviation analysis. The computation processes all bars simultaneously using vectorized numpy operations, ensuring consistent results regardless of the dataset size.

Integer parameters control window lengths and thresholds, allowing the indicator to adapt from scalping on short timeframes to position trading on weekly charts. Shorter windows increase sensitivity to recent price action while longer windows provide smoother, more reliable signals.

Float parameters fine-tune sensitivity and scaling factors. Small adjustments to these values can significantly change signal frequency and quality, so test changes on historical data before applying to live trading.

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback | 50 | 20 - 200 | Controls lookback sensitivity (int) |
| Confidence % | 95.0 | 90.0 - 99.9 | Controls confidence % sensitivity (float) |
| Risk Budget % | 2.0 | 0.5 - 10.0 | Controls risk budget % sensitivity (float) |

## Signals

- **EVaR %**: Primary visual output plotted as a continuous line on the chart
- **Position Size %**: Primary visual output plotted as a continuous line on the chart
- **Normal Risk** (2): Reference level for threshold-based decisions
- **Elevated Risk** (5): Reference level for threshold-based decisions
- **Full Size** (100): Reference level for threshold-based decisions
- **Background shading**: Highlights active signal zones based on high_risk.tolist()

## Python Advantage

The entire computation runs as vectorized numpy operations, processing all bars simultaneously rather than one at a time:

```python
n = len(cl)

log_returns = np.zeros(n)
log_returns[1:] = np.log(cl[1:] / np.where(cl[:-1] > 0, cl[:-1], 1.0))

z = stats.norm.ppf(1 - confidence / 100)

evar = np.zeros(n)
pos_size = np.zeros(n)

for i in range(lookback, n):
```

Python's numpy arrays allow element-wise arithmetic across thousands of bars in a single expression. Adding custom variations or combining with other calculations is straightforward, requiring only standard array operations.

## When to Use

- Size positions based on current risk metrics
- Monitor portfolio drawdown and exposure levels
- Set stop-losses calibrated to actual price volatility
- Evaluate risk-reward ratios before entering trades

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
