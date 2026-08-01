# WaveTrend Enhanced

Enhanced WaveTrend oscillator with channel index smoothing and automated bullish divergence detection using numpy.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Channel Length:** EMA period for the channel index calculation (default: 10)
- **Average Length:** EMA period for the double smoothing step (default: 21)

## Signals

- **WT1 (aqua line):** Primary WaveTrend oscillator line
- **WT2 (orange line):** Signal line (4-period SMA of WT1)
- **Overbought zone:** Above +60
- **Oversold zone:** Below -60
- **Bullish divergence triangles:** Price makes a lower low while WT1 makes a higher low, indicating potential reversal

## Usage

Add this indicator to a subchart. Look for WT1/WT2 crossovers near the overbought or oversold levels. Bullish divergence signals appear as green triangles when price and the oscillator diverge at lows.

## How It Works

1. Compute the channel index: `ci = (close - EMA(close, n1)) / (0.015 * EMA(|close - EMA(close, n1)|, n1))`
2. Apply double EMA smoothing to get WT1
3. Compute WT2 as a 4-period SMA of WT1
4. Detect local minima in both price and WT1, then flag bullish divergences
