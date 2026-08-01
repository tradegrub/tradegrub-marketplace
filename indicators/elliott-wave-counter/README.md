# Elliott Wave Counter

Automated Elliott Wave detection using swing-based pivot analysis. Identifies 5-wave impulse patterns and scores their quality against classic Elliott Wave rules.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Swing Length | int | 10 | 3-50 | Lookback bars for swing pivot detection |

## Signals

- **Wave Number (blue):** Current wave position 1-5 at detected swing points
- **Pattern Score (orange):** Quality score 0-100 based on rule validation
- **Wave 5 diamond:** Completed 5-wave impulse, potential reversal zone
- **Wave 3 triangle:** Strongest wave in the impulse, trend confirmation

## Usage

The indicator detects swing highs and lows, alternates them, then checks sequences of 6 alternating pivots for Elliott Wave compliance. It validates three rules: Wave 2 must not retrace below Wave 1 start, Wave 3 must not be the shortest wave, and Wave 4 must not overlap Wave 1 territory. Higher pattern scores indicate stronger adherence to classic Elliott Wave structure. Use on daily or weekly timeframes for the most reliable wave counts.
