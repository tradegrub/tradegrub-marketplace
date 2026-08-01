# Sentiment Mood Oscillator

Multi-layered sentiment oscillator that combines RSI, MFI, and price momentum into a single "market mood" score ranging from -100 to +100.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **RSI Length:** Period for RSI calculation (default 14)
- **MFI Length:** Period for Money Flow Index (default 14)
- **ROC Length:** Period for Rate of Change momentum (default 10)
- **Smoothing Length:** EMA smoothing applied to the final score (default 5)
- **RSI Weight %:** Weight of RSI component in the composite (default 40)
- **MFI Weight %:** Weight of MFI component in the composite (default 30)
- **ROC Weight %:** Weight of ROC component in the composite (default 30)

## Signals

The oscillator defines five sentiment zones:

- **Euphoria (above +60):** Extreme bullish sentiment, potential overbought conditions
- **Optimism (+20 to +60):** Bullish bias with healthy momentum
- **Neutral (-20 to +20):** No clear directional bias
- **Fear (-60 to -20):** Bearish bias with weakening momentum
- **Panic (below -60):** Extreme bearish sentiment, potential oversold conditions

Background highlights appear during Euphoria and Panic zones to flag extreme readings.

## How It Works

1. RSI, MFI, and Rate of Change are each normalized to a -100 to +100 scale
2. The three components are combined using configurable weights
3. The composite score is smoothed with an EMA to reduce noise
4. The resulting mood line is color-coded by zone: green for bullish, yellow for neutral, red for bearish
