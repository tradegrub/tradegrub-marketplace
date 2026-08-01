# First Passage Time Estimator

Estimates the probability of price reaching upper and lower target levels within a given lookback horizon. Uses geometric Brownian motion assumptions with the reflection principle to compute analytical first passage probabilities. Drift and volatility are estimated from recent log returns.

## Conceptual Diagram

![Concept](concept.svg)

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Target Percent | 5.0 | 1.0-20.0 | Target move size in percent |
| Lookback | 50 | 10-200 | Window for drift/volatility estimation and time horizon |

## Signals

- Upper probability above 50%: more likely than not to reach upside target
- Lower probability above 50%: more likely than not to reach downside target
- Divergence between upper and lower: directional bias in the market
- Both probabilities low: low volatility environment, expect small moves

## Usage

Use to assess whether a target price level is realistically achievable given current market conditions. Helpful for setting profit targets and stop losses. Compare upper vs lower probabilities to gauge directional skew.
