# Stair-Step Trend Detector

Detects orderly stair-step trending where price makes consistent, roughly equal-sized moves followed by consolidation pauses. This pattern indicates institutional accumulation or distribution.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Pivot Length:** Number of bars for swing point detection (default: 5)
- **Min Steps:** Minimum consecutive steps required to confirm a stair pattern (default: 3)
- **Consistency Threshold:** Maximum coefficient of variation allowed for step sizes (default: 0.5, lower means stricter)
- **ATR Length:** Period for ATR calculation (default: 14)
- **Step Line Length:** How far step level lines extend forward (default: 20 bars)

## Signals

- **Stair Score (0-100):** Oscillator measuring the quality of the current stair-step pattern. Higher values indicate more orderly stepping behavior.
- **Green background:** Active uptrend stair-step detected (3+ consistent higher lows with trend alignment).
- **Red background:** Active downtrend stair-step detected (3+ consistent lower highs with trend alignment).
- **Green triangle (below bar):** New upward step confirmed at a higher low.
- **Red triangle (above bar):** New downward step confirmed at a lower high.
- **Horizontal lines:** Mark each confirmed step level.

## How It Works

1. The indicator identifies swing highs and lows using a pivot detection method over the configured pivot length.
2. It measures the distance between consecutive higher lows (uptrend) or lower highs (downtrend) to determine step sizes.
3. Step consistency is calculated as the coefficient of variation (standard deviation divided by mean) of recent step sizes. A lower value means the steps are more uniform.
4. The stair quality score combines three factors: the number of consecutive steps (up to 40 points), step size consistency (up to 40 points), and trend alignment with the moving average (up to 20 points).
5. When enough consistent steps are detected in a trending direction, the indicator highlights the background and marks each new step.

Orderly stair-step patterns often reflect methodical institutional positioning, where large players accumulate or distribute shares in measured increments to avoid moving the price too sharply.
