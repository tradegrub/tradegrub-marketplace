# Gap Closure Probability

Tracks price gaps between open and previous close, measures their historical fill rates, and displays a rolling fill probability percentage.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Lookback | int | 100 | 20-500 | Rolling window for fill rate calculation |
| Fill Window | int | 20 | 5-100 | Bars allowed for a gap to be considered filled |

## Signals

- **Fill Probability (blue):** Rolling percentage of gaps that were filled within the fill window, 0-100
- **Gap Size (orange):** Magnitude of the gap as a percentage, scaled 10x for visibility
- **Green triangle:** Gap that was successfully filled
- **Red diamond:** Gap that remained unfilled within the fill window

## Usage

A high fill probability (above 80%) suggests gaps in this instrument tend to close, supporting fade-the-gap strategies. Low fill probability (below 20%) indicates gaps tend to persist, favoring gap-and-go momentum plays. Monitor unfilled gap markers as potential future support/resistance levels. The fill window parameter controls how many bars a gap has to fill before being marked unfilled.
