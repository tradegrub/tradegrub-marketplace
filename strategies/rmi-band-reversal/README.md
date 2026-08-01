# RMI Band Reversal

Mean reversion strategy that combines the Relative Momentum Index (RMI) with Bollinger Bands applied to the RMI itself. RMI is a variation of RSI that measures price change over N bars (the momentum period) instead of just 1 bar, producing a smoother oscillator that filters out noise.

## Concept

![Concept](concept.svg)

## How It Works

1. **RMI Calculation**: Measures momentum by comparing the current close to the close N bars ago, then smooths gains and losses with an exponential moving average.
2. **Bollinger Bands on RMI**: A moving average and standard deviation envelope applied to the RMI values, creating dynamic overbought/oversold zones that adapt to volatility.
3. **Entry Signals**:
   - **Long**: RMI crosses above the lower Bollinger Band from below while RMI is below 40 (oversold reversal).
   - **Short**: RMI crosses below the upper Bollinger Band from above while RMI is above 60 (overbought reversal).
4. **Exit Signals**:
   - **Exit Long**: RMI rises above 60 or crosses above the middle band.
   - **Exit Short**: RMI drops below 40 or crosses below the middle band.

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| RMI Length | int | 14 | Lookback period for RMI smoothing |
| Momentum Period | int | 5 | Number of bars for momentum comparison |
| BB Length | int | 20 | Bollinger Band moving average length |
| BB Multiplier | float | 2.0 | Standard deviation multiplier for bands |
| Show Labels | bool | true | Display entry/exit labels on chart |

## Best Used For

- Range-bound or choppy markets where price tends to revert to the mean
- Identifying exhaustion points after momentum extremes
- Filtering false RSI signals by using a longer momentum lookback

## Notes

- In strong trending markets, mean reversion signals may trigger too early. Consider combining with a trend filter.
- Shorter momentum periods make RMI behave more like traditional RSI. Longer periods produce smoother, more selective signals.
- Tighter BB multiplier values (1.5) generate more signals; wider values (2.5+) produce fewer but higher-conviction entries.
