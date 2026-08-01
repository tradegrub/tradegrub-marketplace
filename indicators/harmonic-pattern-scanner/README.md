# Harmonic Pattern Scanner

Detects classic harmonic price patterns (Gartley, Butterfly, Bat, Crab) using zigzag swing structure and Fibonacci ratio validation. Completed patterns are drawn directly on the price chart with labeled XABCD points.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Zigzag Length:** Number of bars to look left and right when identifying swing highs and lows. Larger values find broader swings, smaller values find tighter patterns.
- **Ratio Tolerance:** How much flexibility to allow when matching Fibonacci ratios. Default is 10%. Increase for more detections, decrease for stricter matching.
- **Min Bars Per Leg:** Minimum number of bars required between each swing point. Filters out noise from very short-term price movements.

## Signals

- **Gartley (green):** B retraces 61.8% of XA, D completes at 78.6% of XA. A reliable reversal pattern.
- **Butterfly (blue):** B retraces 78.6% of XA, D extends to 127% of XA. An extension pattern signaling potential reversals.
- **Bat (orange):** B retraces 38.2% to 50% of XA, D completes at 88.6% of XA. A deep retracement pattern.
- **Crab (pink):** B retraces 38.2% to 61.8% of XA, D extends to 161.8% of XA. The most extended harmonic pattern.

## How It Works

1. The indicator scans price action for swing highs and swing lows using a zigzag algorithm based on the configured length.
2. Groups of five consecutive alternating swings are evaluated as potential XABCD patterns.
3. Fibonacci ratios between the legs (XA, AB, BC, CD) are compared against known harmonic pattern definitions.
4. When ratios fall within the configured tolerance, the pattern is drawn on the chart with connecting lines and point labels.
5. The pattern name is displayed at the D (completion) point.
