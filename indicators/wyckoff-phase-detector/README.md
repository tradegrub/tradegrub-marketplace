# Wyckoff Phase Detector

Detects Wyckoff accumulation and distribution phases by analyzing volume patterns, price range structure, and key events like springs and upthrusts.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Lookback Period:** Number of bars to define the trading range (default: 50)
- **Volume MA Length:** Period for the volume moving average used in comparisons (default: 20)
- **Spring/Upthrust Threshold:** Percentage beyond support/resistance to qualify as a spring or upthrust (default: 0.02, meaning 2%)

## Signals

- **Phase Score (gold line):** Oscillates between -100 and +100. Positive values indicate accumulation, negative values indicate distribution.
- **Spring (green triangle below bar):** Price dips below support and recovers on above-average volume. A classic accumulation signal.
- **Upthrust (red triangle above bar):** Price breaks above resistance and fails on above-average volume. A classic distribution signal.
- **Background shading:** Green tint when the phase score is above +20 (accumulation zone), red tint when below -20 (distribution zone).
- **Horizontal lines:** Reference levels at 0 (neutral), +50 (strong accumulation), and -50 (strong distribution).

## How It Works

1. The indicator establishes a trading range using the highest high and lowest low over the lookback period.
2. It compares volume on up bars versus down bars. In accumulation, volume tends to be higher on rallies and lower on pullbacks. In distribution, the pattern reverses.
3. Springs are detected when price briefly penetrates below support by the threshold percentage, then closes back inside the range on elevated volume.
4. Upthrusts are detected when price briefly penetrates above resistance by the threshold percentage, then closes back inside the range on elevated volume.
5. These signals are combined into a composite phase score, smoothed over 5 bars for readability.
