# TradeGrub Marketplace

Community marketplace for TradeGrub Charts strategies and indicators. Browse, share, and install free trading strategies with built-in backtesting.

## Folder Structure

```text
tradegrub-marketplace/
  manifest.schema.json        # JSON Schema for manifest validation
  CONTRIBUTING.md              # How to add strategies
  strategies/
    ma-crossover/              # Moving Average Crossover
    bollinger-bands/           # Bollinger Bands
    rsi-mean-reversion/        # RSI Mean Reversion
    supertrend/                # Supertrend
    macd-crossover/            # MACD Crossover
  indicators/                  # (coming soon)
  .github/ISSUE_TEMPLATE/      # Bug reports, features, submissions
```

Each strategy folder contains:

- `manifest.json` -- metadata, version, category, tags
- `strategy.py` -- Python script using the `tg_scripting` API
- `README.md` -- documentation, parameters, signals

## Browse Strategies

Open any strategy folder to read its README, view the source code, and see parameter defaults. All seed strategies are open-source and free.

## Install a Strategy

Copy the `strategy.py` contents into the TradeGrub script editor, or install directly from the in-app marketplace.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on adding your own strategies and indicators.

## License

Apache 2.0. See [LICENSE](LICENSE) for details.
