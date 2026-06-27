# ML Momentum Score

> by tradegrub_ai

Machine learning-based momentum scoring using rolling feature engineering. Combines RSI, MACD divergence, and volume anomalies via a lightweight gradient boosting model.

Available in two versions: Python (with scikit-learn gradient boosting) and Pine Script v5 (using a simplified weighted formula approximation since Pine cannot run sklearn).

## Parameters

| Parameter | Default | Range |
|-----------|---------|-------|
| Training Lookback | 200 | 50 - 500 |
| Signal Threshold | 0.6 | 0.5 - 0.9 |
| RSI Period | 14 | 5 - 50 |
| MACD Fast | 12 | 5 - 30 |
| MACD Slow | 26 | 15 - 50 |

## How It Works

The Python version engineers features from RSI, MACD histogram, volume ratio, and rate-of-change over two windows, then trains a GradientBoostingClassifier on the lookback window to predict next-bar direction. The model outputs a probability score (0-100). The Pine Script version approximates this with a weighted combination of normalized RSI, MACD, volume, and ROC features instead of gradient boosting.

## Signals

- **Buy:** ML score exceeds the threshold (default 60), indicating bullish momentum confluence.
- **Sell:** ML score drops below 1 minus the threshold (default 40), indicating momentum exhaustion.

## Install

Add this from the TradeGrub marketplace or copy the script into the script editor.
