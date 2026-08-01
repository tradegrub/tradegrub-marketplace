# Sequential Exhaustion Counter

DeMark-style sequential counting system that identifies potential trend exhaustion points through two phases: Setup (1-9) and Countdown (1-13).

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| (none) | — | — | No user inputs required |

## Signals

- **Setup Count (blue):** Consecutive bars where close > close[4] (bullish, positive) or close < close[4] (bearish, negative), counting to 9
- **Countdown (orange):** After a completed 9-count, counts bars where close > high[2] (sell) or close < low[2] (buy), up to 13
- **Bullish 9 triangle:** A completed bullish setup count, potential exhaustion
- **Bearish 9 triangle:** A completed bearish setup count, potential exhaustion
- **Diamond markers:** Completed 13-count countdown, stronger exhaustion signal

## Usage

A completed 9-count setup warns of possible trend fatigue. The subsequent 13-count countdown provides confirmation. Look for completed counts near support/resistance levels for higher probability reversal signals. The setup resets if the consecutive comparison sequence breaks.
