# Safety Order DCA

Dollar cost averaging strategy with configurable safety orders.

## Concept

![Concept](concept.svg)

## How it works

1. **Base order**: Opens a long position when price crosses below the SMA.
2. **Safety orders**: If price continues to drop, additional buy orders are placed at progressively lower levels. Each safety order uses a larger position size (scaled by the volume scale factor), lowering the average entry price.
3. **Take profit**: When price reaches the target profit percentage above the average entry price, the entire position is closed.

## Inputs

- **Initial Drop %**: Percentage below the base entry for the first safety order (default: 1.0)
- **Safety Order Step %**: Base percentage distance between consecutive safety orders (default: 1.5)
- **Step Scale**: Multiplier applied to the step distance for each subsequent order (default: 1.5)
- **Volume Scale**: Multiplier applied to the position size for each subsequent order (default: 1.5)
- **Target Profit %**: Percentage above the average entry price to trigger a full exit (default: 2.0)
- **Max Safety Orders**: Maximum number of safety orders per deal (default: 5)
- **SMA Length**: Period for the simple moving average used as the entry trigger (default: 50)

## Example

With default settings and an initial buy at $100:

| Order | Trigger Price | Size |
|-------|--------------|------|
| Base  | $100.00      | 1.0x |
| SO 1  | $99.00       | 1.5x |
| SO 2  | $97.50       | 2.3x |
| SO 3  | $94.13       | 3.4x |
| SO 4  | $88.44       | 5.1x |
| SO 5  | $79.22       | 7.6x |

The strategy exits all positions when the price rises to the target profit percentage above the volume-weighted average entry.

## Notes

- Works best in ranging or mean-reverting markets where temporary dips recover.
- In strong downtrends, all safety orders may fill without reaching the take profit target. Consider using the max safety orders setting to limit exposure.
- The step scale and volume scale inputs control how aggressively the strategy accumulates at lower prices.
