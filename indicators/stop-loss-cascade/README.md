# Stop Loss Cascade Detector

Identifies where stop loss orders likely cluster near swing highs and lows, and measures the potential for a cascade breakout when price approaches those zones.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

1. Identifies swing highs and lows within the lookback window using numpy
2. Groups nearby swing levels into clusters (within ATR multiple)
3. Measures cascade intensity: how many stop levels stack in a tight range
4. Tracks proximity of current price to the nearest cluster zone

## Parameters

- **Swing Lookback** (default 20): Number of bars to scan for swing points
- **Cluster ATR Mult** (default 0.5): ATR multiple defining cluster proximity threshold

## Signals

- **Cascade Intensity > 70**: Multiple stop levels stacked tightly, high cascade risk
- **Proximity rising**: Price approaching a dense stop cluster
- **Background highlight**: Red tint when cascade intensity is elevated

## Usage

Use to anticipate sharp moves caused by stop loss cascades. When intensity is high and price is near a cluster, expect acceleration through the zone. Useful for timing breakout entries or avoiding false breakouts.
