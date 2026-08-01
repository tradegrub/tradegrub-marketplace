# Volume Surprise Detector

Detects statistically significant volume deviations using z-score analysis. Flags bars where actual volume departs meaningfully from what is statistically expected, distinguishing between positive surprises (unusual interest) and negative surprises (unusual quiet).

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Lookback Period:** Number of bars used to calculate the expected volume and standard deviation (default 20).
- **Surprise Threshold:** Z-score threshold for flagging a volume surprise (default 2.0). Higher values require more extreme deviations.

## Signals

- **Green triangle (below bar):** Positive surprise. Volume is significantly higher than expected, suggesting unusual buying or selling interest.
- **Red triangle (above bar):** Negative surprise. Volume is significantly lower than expected, suggesting unusual quiet or lack of participation.
- **Green background tint:** Extreme positive surprise (z-score exceeds threshold + 1).
- **Red background tint:** Extreme negative surprise (z-score below negative threshold - 1).

## How It Works

1. Calculate the expected volume as the simple moving average of volume over the lookback period.
2. Compute the standard deviation of volume over the same window.
3. Derive the z-score: (actual volume - expected volume) / standard deviation.
4. A z-score above the threshold marks a positive surprise. A z-score below the negative threshold marks a negative surprise.
5. The z-score is plotted as an oscillator around zero, with horizontal reference lines at the threshold levels.
