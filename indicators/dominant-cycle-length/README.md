# Dominant Cycle Length

![Concept](concept.svg)

Reports the dominant cycle length and current phase position using autocorrelation analysis. Detrends price data, then finds the lag with the highest positive autocorrelation to identify the dominant repeating cycle.

## How It Works

- Detrends price using linear regression to remove trend bias
- Computes autocorrelation at lags from 5 to the configured max period
- The lag with the highest autocorrelation is the dominant cycle length
- Phase tracks the current position within the cycle (0-360 degrees) based on distance from the last cycle peak

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Max Period | 60 | 20-120 | Maximum lag to search for the dominant cycle |

## Outputs

- **Cycle Length**: Green line showing the detected dominant cycle period in bars
- **Phase**: Purple line showing current position in the cycle (0-360 degrees)
- **Zero Line**: Gray baseline

## Usage Notes

- Stable cycle length readings indicate a strong periodic pattern in price
- Phase near 0/360 suggests a cycle peak; phase near 180 suggests a cycle trough
- Rapidly changing cycle length indicates no dominant periodicity is present
- Works best on instruments with regular seasonal or institutional trading patterns
