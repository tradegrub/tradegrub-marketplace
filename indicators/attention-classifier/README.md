# Attention State Classifier

Transformer-inspired soft attention mechanism for historical state matching. Computes a directional prediction score by finding similar past market states and weighting their outcomes.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Lookback** (default 100): Number of historical bars to search for pattern matches

## How It Works

For each bar, the indicator builds a 4-dimensional feature vector:
- Normalized RSI (0 to 1)
- Normalized ATR (as percentage of price)
- Volume ratio (current volume vs 20-bar average)
- Price position within 20-bar range (0 to 1)

It then computes dot-product similarity between the current feature vector and every historical bar in the lookback window. Softmax converts similarities to attention weights. The weighted average of forward returns after each historical bar produces the prediction score, scaled to basis points and clamped to -100 to 100.

## Signals

- **Score above 50**: Strong bullish historical pattern match (green background)
- **Score below -50**: Strong bearish historical pattern match (red background)
- **Score near zero**: No strong directional pattern detected

## Usage

Use as a supplementary signal alongside trend and momentum indicators. High absolute scores indicate the current market state closely matches past states that preceded directional moves. Not a standalone trading signal.
