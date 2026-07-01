# Andean Oscillator

Exponential envelope oscillator that decomposes price action into bull and bear components using open-close differences with cross-suppression.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Length | int | 50 | 5-200 | EMA smoothing period |
| Alpha | float | 0.5 | 0.0-1.0 | Cross-suppression factor |

## Signals

- Bull line above zero: buying pressure dominates
- Bear line above zero: selling pressure dominates
- Signal line (bull minus bear) crossing zero: trend shift
- Higher alpha increases suppression of the opposing component

## Usage

Watch for signal line zero-crossovers to identify trend changes. When bull and bear lines diverge, the trend is strong. Convergence suggests consolidation. The alpha parameter controls how aggressively each component suppresses the other.
