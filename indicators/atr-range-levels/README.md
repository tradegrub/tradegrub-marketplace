## ATR Range Levels

Projects the likely daily price range using Average True Range. A smoothed reference price anchors the center, then ATR is added and subtracted to create upper and lower range boundaries. When price approaches these levels, it suggests the daily move may be nearing exhaustion.

### Parameters

- **ATR Length**: Period for ATR calculation (default: 14)
- **Multiplier**: Scales the ATR distance from reference (default: 1.0)
- **Show 50% Levels**: Display intermediate range targets at half the ATR distance (default: on)

### How It Works

1. A smoothed reference price (SMA over the ATR period) anchors the range center
2. ATR measures average volatility over the configured period
3. Upper level: reference + ATR x multiplier
4. Lower level: reference - ATR x multiplier
5. Optional 50% levels mark intermediate targets

### Reading the Indicator

- **Red line (upper)**: Price reaching this level has covered the expected daily range to the upside
- **Green line (lower)**: Price reaching this level has covered the expected daily range to the downside
- **Blue line (reference)**: Smoothed anchor price
- **Orange lines (50%)**: Intermediate range targets, useful for partial profit-taking
- **Red background tint**: Price is near the ATR range limit (80%+ of range used)
- **Orange background tint**: Price is approaching the midpoint of the range (40-80%)

### Use Cases

- Estimating how much room a move has left on the current day
- Setting profit targets based on statistical range expectations
- Filtering late entries when price has already used most of its expected range


## Conceptual Diagram

![Concept](concept.svg)
