# Liquidity Flow Proxy

Approximates macro liquidity conditions using price-volume dynamics. Computes cumulative directional volume as a proxy for money flow in and out of the market.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

- **Lookback** (default 50): Rolling window for normalizing the liquidity flow calculation

## How It Works

Each bar's volume is signed based on the close-to-open direction: positive if the bar closed above open (buying pressure), negative if below (selling pressure). This signed volume is accumulated over the lookback window and normalized by average volume to produce a liquidity flow score.

A 20-period SMA of the flow provides the smoothed trend.

## Signals

- **Liquidity flow rising above zero**: Money flowing in, bullish undertone (cyan background)
- **Liquidity flow falling below zero**: Money flowing out, bearish undertone (orange background)
- **Divergence from price**: Liquidity flow falling while price rises suggests weakening support for the move
- **Flow crossing SMA**: Momentum shift in liquidity direction

## Usage

Use as a volume-based confirmation tool. When liquidity flow aligns with price direction, moves have stronger conviction. Divergences between liquidity flow and price often precede reversals. Particularly useful for identifying whether a breakout has real volume support.
