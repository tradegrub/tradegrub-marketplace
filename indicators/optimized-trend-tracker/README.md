# Optimized Trend Tracker

Percentage-based optimized trailing trend indicator using EMA with adaptive bands. The OTT line tracks price direction by switching between upper and lower percentage bands around an EMA, holding the previous value when price stays within the bands.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Length:** EMA smoothing period (default: 20, range: 5 to 100)
- **Percent:** Band width as percentage of EMA (default: 2.0, range: 0.1 to 10.0)

## Signals

- **Green line (OTT Bull):** Price is above the OTT, indicating bullish trend
- **Red line (OTT Bear):** Price is below the OTT, indicating bearish trend
- Color change from red to green signals a potential trend reversal to the upside
- Color change from green to red signals a potential trend reversal to the downside

## Usage

1. Add the indicator to your chart (overlay on price)
2. Adjust the Length parameter for faster or slower trend detection
3. Increase the Percent parameter to filter out noise in volatile markets
4. Decrease the Percent parameter for tighter trend tracking in calm markets
5. Use color changes as entry and exit signals, or combine with other indicators for confirmation
