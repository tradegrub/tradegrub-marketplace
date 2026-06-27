# Contributing to TradeGrub Marketplace

## Adding a Strategy

1. Create a new folder under `strategies/` using kebab-case (e.g. `strategies/my-strategy/`).
2. Add three files inside the folder:
   - **manifest.json** -- metadata for the marketplace (must validate against `manifest.schema.json`)
   - **strategy.py** -- Python script using the `tg_scripting` API
   - **README.md** -- documentation with parameters table, how it works, and signals

## Naming Conventions

- Folder names: kebab-case (`bollinger-bands`, not `BollingerBands`)
- Strategy IDs in manifest.json must match the folder name

## Manifest Schema

All manifest.json files must conform to the root `manifest.schema.json`. Required fields:

| Field                | Type     | Notes                                      |
|----------------------|----------|--------------------------------------------|
| id                   | string   | Kebab-case, matches folder name            |
| name                 | string   | Display name                               |
| author               | string   | Author display name                        |
| author_uid           | string   | Author unique identifier                   |
| version              | string   | Semver (e.g. "1.0.0")                      |
| category             | string   | trend, mean-reversion, momentum, volatility, volume |
| tags                 | string[] | Searchable keywords                        |
| type                 | string   | "strategy" or "indicator"                  |
| access               | string   | open-source, free, or paid                 |
| price                | number   | 0 for free/open-source                     |
| currency             | string   | "USD"                                      |
| description          | string   | One sentence, max 280 chars                |
| min_platform_version | string   | Minimum TradeGrub platform version         |
| screenshots          | string[] | URLs to screenshot images                  |
| backtest_summary     | object   | Summary stats from backtesting             |
| created              | string   | ISO date (YYYY-MM-DD)                      |
| updated              | string   | ISO date (YYYY-MM-DD)                      |

## Testing

1. Validate your manifest: ensure it passes the JSON Schema in `manifest.schema.json`.
2. Load your `strategy.py` in the TradeGrub script editor and run a backtest.
3. Verify plots render correctly on the chart.

## Submitting

Open a pull request with your new strategy folder. Alternatively, use the **Strategy Submission** issue template.
