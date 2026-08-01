# Kinetic Slippage Index

Quantifies the gap between expected and actual price movement based on volume.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

1. Computes average ATR and average volume over the lookback period
2. Expected movement: volume_ratio (current/average) multiplied by average ATR
3. Actual movement: absolute difference between close and open
4. Slippage: percentage difference between expected and actual movement

High slippage means volume came in but price did not move proportionally, indicating absorption by large players or market inefficiency.

## Parameters

- **Lookback Period** (default 20): Period for computing averages and smoothing

## Signals

- High slippage (above 50): Volume is being absorbed without proportional price movement, potential accumulation/distribution
- Low slippage (near 0 or negative): Price is moving efficiently with volume, trending conditions
- Rising slippage during a trend can signal upcoming reversal as opposing force absorbs momentum

## Usage

Use to detect hidden accumulation or distribution. When slippage is high, large players may be absorbing supply or demand without letting price move. This often precedes significant moves when the absorption phase ends.
