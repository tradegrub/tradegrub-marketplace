# Decennial Cycle Projection

Maps historical returns by position within a configurable long cycle to project seasonal tendencies.

## Conceptual Diagram

![Concept](concept.svg)

## How It Works

1. Computes bar-to-bar returns across all available history
2. Groups returns by their position within the cycle (e.g., bar 1 of 252, bar 2 of 252, etc.)
3. Averages returns at each cycle position across all complete cycles
4. Smooths the pattern and computes a cumulative seasonal score
5. Projects the score forward based on the current cycle position

## Parameters

- **Cycle Length** (default 252): Number of bars per cycle. 252 approximates one trading year on daily charts.

## Signals

- Score above 50: Historically bullish cycle position
- Score below -50: Historically bearish cycle position
- Rising score: Approaching a historically favorable period
- Falling score: Approaching a historically weak period

## Usage

Use to identify seasonal or cyclical tendencies in a security. The default 252-bar cycle captures annual seasonality on daily charts. Adjust the cycle length for other timeframes or to explore multi-year patterns. Best used as a secondary confirmation tool rather than a primary signal.
