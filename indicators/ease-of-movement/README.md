# Ease of Movement

Classic EMV indicator that measures how easily price moves relative to volume. High positive values indicate price advancing on low volume (easy upward movement). Negative values indicate downward pressure.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Type | Default | Range | Description                    |
|-----------|------|---------|-------|--------------------------------|
| Length    | int  | 14      | 2-100 | Smoothing period for EMV and signal |

## Signals

- **EMV (blue):** Smoothed Ease of Movement value
- **Signal (orange):** Double-smoothed EMV acting as a signal line
- **Green background:** EMV above zero and above signal (bullish)
- **Red background:** EMV below zero and below signal (bearish)

## Usage

EMV combines price change direction with volume to show movement efficiency. When EMV is positive and rising, price is moving up easily on relatively low volume. Crossovers of EMV above the signal line confirm bullish momentum. Zero-line crossings indicate directional shifts. Divergences between EMV and price can signal weakening trends.
