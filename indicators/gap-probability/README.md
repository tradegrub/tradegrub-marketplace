# Movement Probability

![Concept](concept.svg)

Estimates the probability of the next bar moving up or down based on historical price behavior at similar z-score levels relative to a moving average.

## How It Works

- Computes the z-score of price relative to its SMA
- Bins z-scores into ranges and looks at historical instances in the same bin
- Counts what percentage of similar z-score situations led to up vs down moves
- Plots both probabilities as complementary lines summing to 100%

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| MA Length | 20 | 5-100 | Period for the SMA and standard deviation |
| Lookback | 200 | 50-500 | Historical window for probability calculation |

## Outputs

- **Up Probability**: Green line showing chance of next bar up (0-100%)
- **Down Probability**: Red line showing chance of next bar down (0-100%)
- **Neutral**: Gray dashed line at 50%
- **High Probability**: Orange dashed line at 65%

## Usage Notes

- Probabilities above 65% indicate a statistical edge from historical patterns
- Works best in mean-reverting conditions; trending markets may show persistent bias
- Not a standalone signal; use to filter entries from other indicators
