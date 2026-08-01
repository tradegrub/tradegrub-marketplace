# Volatility Contraction Pattern (VCP)

Detects when a stock is forming progressively tighter price ranges with declining volume, a setup that often precedes a breakout.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Range Period:** Length for measuring the short-term price range (default: 10)
- **Base Period:** Length for measuring the longer base range and ATR (default: 40)
- **Volume Period:** Length for the short-term volume average (default: 20)
- **Contraction Threshold:** How tight the range ratio must be to qualify as contracting (default: 0.5)

## Signals

- **Cyan background highlight:** Active VCP zone where price range and volume are both contracting
- **Orange line:** Breakout level (highest high of the range period), shown only during VCP zones
- **Green triangle:** Start of a new VCP zone

## How It Works

The indicator tracks three contraction measures at once:

1. **Range contraction:** The short-period high-low range divided by the base-period range. When this ratio drops below the contraction threshold, the price range is tightening.
2. **ATR contraction:** Short ATR vs long ATR. A ratio below 0.7 confirms reduced bar-to-bar volatility.
3. **Volume contraction:** Short volume SMA vs long volume SMA. A ratio below 0.8 shows declining participation.

When all three conditions are true simultaneously, the indicator highlights the zone and plots the breakout level. A triangle marks the first bar of each new VCP zone. Watch for price to break above the orange breakout level on increasing volume for a potential entry.
