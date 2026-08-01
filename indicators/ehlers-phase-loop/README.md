# Phase Loop Oscillator

Price-volume quadrant analysis oscillator that detects accumulation and distribution phases by combining price momentum with volume momentum.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Length:** Lookback period for rate of change calculation (default: 14)

## Signals

The indicator divides price-volume action into four quadrants:

- **Q1 (green background):** Price up, volume up. Accumulation phase with strong buying pressure.
- **Q2 (yellow background):** Price up, volume down. Distribution warning, rally losing steam.
- **Q3 (red background):** Price down, volume down. Distribution phase, sellers in control.
- **Q4 (blue background):** Price down, volume up. Panic selling or early accumulation start.

Two normalized momentum lines are plotted:

- **Price Momentum (green line):** Normalized rate of change of price, scaled to -1 to 1.
- **Volume Momentum (blue line):** Normalized rate of change of volume, scaled to -1 to 1.

## Usage

Look for transitions between quadrants to identify shifts in market structure. A move from Q3 to Q4 often signals capitulation. A move from Q4 to Q1 confirms accumulation is underway. Sustained time in Q2 warns that a trend reversal may be approaching.
