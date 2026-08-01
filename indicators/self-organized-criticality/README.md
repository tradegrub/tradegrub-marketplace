# Market Criticality Index

Measures market fragility using concepts from complexity science. Combines three components into a single 0-100 score: tail risk (percentage of returns exceeding a standard deviation threshold), volatility clustering (autocorrelation of squared returns), and range compression (current range vs average range). High readings suggest the market is in a fragile, critical state prone to sudden large moves.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Lookback Length | 50 | 10-200 | Rolling window for all calculations |
| Tail Threshold | 2.0 | 1.0-4.0 | Standard deviations for tail risk detection |

## Signals

- Criticality above 70: market is in a fragile state, expect large moves
- Criticality below 30: market is in a stable state
- Rising criticality with compressed ranges: potential breakout setup
- Background shading appears when criticality exceeds the danger zone

## Usage

Use as a regime filter to avoid mean-reversion strategies during critical periods, or to prepare for breakout trades when criticality is elevated. Works on all timeframes and instruments.
