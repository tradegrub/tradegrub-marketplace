# Markov Regime Strategy

A statistical trading strategy that uses Markov chain transition probability matrices to identify market regimes (bull, bear, neutral) and generate trading signals based on regime state changes.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

The strategy discretizes price returns into three states: bull (returns above a threshold), bear (returns below the negative threshold), and neutral (everything in between). Over a rolling window, it counts the transitions between these states and builds a 3x3 transition probability matrix. Each row of the matrix represents the current state, and each column represents the probability of transitioning to the next state.

Using the transition matrix, the strategy computes the probability of moving into each regime from the current state. When the probability of entering a bull regime exceeds the entry threshold, a long position is initiated. When the bear regime probability crosses above the threshold, a short position is opened. Positions are exited when the opposing regime probability rises or when ATR-based stop-loss and take-profit levels are hit.

The core advantage of this approach is that it captures the statistical tendency of markets to persist in regimes. Rather than reacting to a single indicator crossing, the strategy evaluates the likelihood of regime persistence or transition based on observed historical behavior within the rolling window.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Return Length | 10 | Number of bars for return calculation |
| State Threshold % | 0.5 | Percentage threshold for bull/bear state classification |
| Rolling Window | 50 | Number of bars used to build the transition matrix |
| Entry Probability | 0.6 | Minimum regime probability required for entry |
| ATR Length | 14 | Period for Average True Range calculation |
| ATR Stop Multiple | 2.0 | ATR multiplier for stop-loss distance |
| Take Profit Ratio | 2.0 | Multiplier applied to stop distance for take-profit |
| Show Labels | True | Display regime and signal labels on chart |
| Show Entry/Stop/TP Levels | True | Display entry, stop-loss, and take-profit lines |

## Signals

- **Long Entry**: Green triangle below bar when bull regime probability crosses above the entry threshold
- **Short Entry**: Red triangle above bar when bear regime probability crosses above the entry threshold
- **Background Zones**: Green tint for bull-dominant regime, red tint for bear-dominant regime, blue tint for neutral
- **State Labels**: Small labels marking regime transitions on the chart
- **Level Annotations**: Dashed lines and boxes showing entry, stop-loss, and take-profit levels

## Python Advantage

Building the transition probability matrix in Python with NumPy is straightforward and efficient:

```python
# Build transition count matrix from rolling window
trans = np.zeros((3, 3))
for j in range(i - window, i):
    trans[states[j - 1], states[j]] += 1

# Normalize rows to get transition probabilities
row_sums = trans.sum(axis=1)
prob_matrix = np.zeros((3, 3))
for r in range(3):
    if row_sums[r] > 0:
        prob_matrix[r] = trans[r] / row_sums[r]

# Current state -> next state probabilities
cur = states[i]
bear_prob = prob_matrix[cur, 0]
neutral_prob = prob_matrix[cur, 1]
bull_prob = prob_matrix[cur, 2]
```

This kind of matrix construction and row normalization is natural in Python but would be difficult to express in traditional Pine.

## Usage Notes

- A larger rolling window produces more stable transition probabilities but responds more slowly to regime changes.
- Lower state thresholds create more frequent state transitions, while higher thresholds produce fewer but more decisive regime shifts.
- The entry probability parameter controls trade frequency: higher values produce fewer but higher-conviction entries.
- Works well on daily and 4-hour timeframes where regime persistence is more pronounced.

## Risk Management

Each trade uses ATR-based stop-loss and take-profit levels. The stop is placed at the entry price minus (or plus, for shorts) the ATR multiplied by the stop multiple. The take-profit is set at a ratio of the stop distance. Positions are also closed when the opposing regime probability rises above the entry threshold, providing a regime-aware exit mechanism.

## Combining with Other Indicators

- **Volume Profile**: Use volume confirmation to validate regime transitions and filter out low-conviction signals.
- **RSI or Stochastic**: Add momentum filters to avoid entering during exhaustion moves within a regime.
- **Moving Averages**: Use a trend filter (e.g., 200 SMA) to only take long signals above the average and short signals below it.
- **Volatility Bands**: Combine with Bollinger Bands or Keltner Channels to identify regime transitions that coincide with volatility expansion.
