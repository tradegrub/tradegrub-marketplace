# Contributing to TradeGrub Marketplace

Thank you for contributing to the TradeGrub Marketplace. This guide covers everything you need to submit a new strategy or indicator.

## Before You Start

- Browse existing scripts in `strategies/` and `indicators/` for reference
- Read a few README files to understand the documentation standard
- Make sure your script works in the TradeGrub script editor before submitting

## Folder Structure

Every script lives in its own folder under `strategies/` or `indicators/`:

```text
strategies/my-strategy/
  manifest.json      # Required: metadata for the marketplace
  strategy.py        # Required: Python script using the tg_scripting API
  README.md          # Required: documentation with parameters, signals, usage
  concept.svg        # Required: visual diagram (800x500, dark theme)
```

```text
indicators/my-indicator/
  manifest.json      # Required: metadata for the marketplace
  indicator.py       # Required: Python script using the tg_scripting API
  README.md          # Required: documentation with parameters, outputs, usage
  concept.svg        # Required: visual diagram (800x500, dark theme)
```

## Naming Conventions

- Folder names: kebab-case (`bollinger-bands`, not `BollingerBands`)
- The `id` field in manifest.json must match the folder name exactly
- Script file must be named `strategy.py` for strategies or `indicator.py` for indicators

## Manifest Schema

All manifest.json files must conform to the root `manifest.schema.json`. Required fields:

| Field                | Type     | Notes                                      |
|----------------------|----------|--------------------------------------------|
| id                   | string   | Kebab-case, matches folder name            |
| name                 | string   | Display name shown in marketplace          |
| author               | string   | Author display name                        |
| author_uid           | string   | Author unique identifier                   |
| version              | string   | Semver (e.g. "1.0.0")                      |
| category             | string   | trend, mean-reversion, momentum, volatility, volume, statistical, pattern |
| tags                 | string[] | Searchable keywords (5-10 recommended)     |
| type                 | string   | "strategy" or "indicator"                  |
| access               | string   | open-source, free, or paid                 |
| price                | number   | 0 for free/open-source                     |
| currency             | string   | "USD"                                      |
| description          | string   | One sentence, max 280 chars                |
| official             | boolean  | false for community submissions            |
| language             | string   | "Python" or "Pine"                         |
| languages            | string[] | ["python"] or ["pine"]                     |
| min_platform_version | string   | Minimum TradeGrub platform version         |
| screenshots          | string[] | URLs to screenshot images                  |
| backtest_summary     | object   | Summary stats from backtesting             |
| created              | string   | ISO date (YYYY-MM-DD)                      |
| updated              | string   | ISO date (YYYY-MM-DD)                      |

## Writing the Script

### Available Packages

The following Python packages are available:

- **numpy** -- always loaded
- **pandas** -- loaded on demand when imported
- **scipy** -- loaded on demand when imported
- **scikit-learn** -- loaded on demand when imported (import as `sklearn`)
- **matplotlib** -- loaded on demand when imported
- **lightgbm** -- loaded on demand when imported
- **xgboost** -- loaded on demand when imported

Packages not listed above (e.g. tensorflow, pytorch) are not available.

### Script Guidelines

1. Use the `tg_scripting` API for all chart interactions (plotting, labels, signals)
2. Define configurable parameters with sensible defaults at the top of your script
3. Handle edge cases: short data, missing values, division by zero
4. Keep computation efficient: scripts run on the user's device
5. Add descriptive labels and annotations to plots so users understand the output
6. For strategies: include clear entry/exit signals with stop loss and take profit levels
7. For indicators: plot all output series with distinct colors and a legend

### Code Quality

- No hardcoded symbols or timeframes: scripts must work on any symbol/resolution
- No external API calls or network requests: scripts only have access to OHLCV data
- No infinite loops or unbounded recursion
- Avoid excessive memory usage: users may have limited device resources
- Use meaningful variable names: the script source is visible to all users

## Writing the README

Every script must include a README.md with the following sections:

1. **Title and one-line description**
2. **Concept diagram** -- `![Concept](concept.svg)` at the top
3. **How It Works** -- explain the logic in plain language
4. **Parameters** -- table with name, default value, and description for each parameter
5. **Signals** (strategies) or **Outputs** (indicators) -- what the script plots/returns
6. **Usage Notes** -- tips for best timeframes, asset classes, or configuration

Keep language simple and direct. No em dashes, no marketing language.

## Creating the Concept Diagram

Every script must include a `concept.svg` file:

- ViewBox: 800x500
- Dark theme: background gradient from #1a1a2e to #16213e
- Include: candlesticks, indicator overlays or sub-pane plots, annotations, volume bars, legend
- Colors: green (#26a69a) for bullish, red (#ef5350) for bearish, blue (#42a5f5) for neutral indicators
- Add a title and "tradegrub.finance" subtitle
- See existing concept.svg files for reference

## Testing and Validation

### Step 1: Manual Testing

Load your script in the TradeGrub script editor at [tradegrub.finance](https://tradegrub.finance):

- Run it on at least 3 different symbols (stock, crypto, index)
- Test on multiple timeframes (1m, 15m, 1H, 1D)
- Verify all plots render correctly on the chart
- For strategies: run a backtest and confirm signals fire correctly
- Check that labels and annotations display without overlap

### Step 2: Automated Validation

Run the validation gate to compile and execute your script against synthetic OHLCV data:

```bash
# Validate a single script
python validate_scripts.py strategies/my-strategy

# Validate all scripts
python validate_scripts.py
```

The validator:
- Imports and compiles your script
- Executes it against 200 bars of synthetic OHLCV data
- Catches any runtime errors, import failures, or exceptions
- Reports pass/fail with error details

Your script must pass validation before it can be merged.

### Step 3: Manifest Validation

Verify your manifest.json conforms to the schema:

- The `id` field matches your folder name
- The `type` field matches whether it is in `strategies/` or `indicators/`
- All required fields are present and correctly typed
- Tags are relevant and descriptive

### Common Validation Failures

| Issue | Fix |
|-------|-----|
| ImportError for pandas/scipy/sklearn | These are available but must be imported correctly (e.g. `from sklearn.cluster import KMeans`) |
| IndexError on short data | Add a guard: `if len(close) < period: return` |
| Division by zero | Check denominators before dividing |
| Missing manifest.json | Every script folder must include manifest.json |
| Missing concept.svg | Every script folder must include concept.svg |
| ID mismatch | manifest.json `id` must match the folder name exactly |

## Adding to the Index

After creating your script folder, add an entry to the root `index.json` file. The entry must include all fields from your manifest.json plus a `path` field pointing to your script folder.

## Submitting

1. Fork this repository
2. Create your script folder with all required files
3. Run `python validate_scripts.py` and confirm your script passes
4. Open a pull request with your new script folder
5. Fill in the PR template with a description and test results

Alternatively, use the **Strategy Submission** or **Indicator Submission** issue template to propose a script idea before building it.

## Review Checklist

Pull requests are reviewed against this checklist:

- [ ] Folder name is kebab-case and matches manifest.json `id`
- [ ] manifest.json validates against manifest.schema.json
- [ ] Script compiles and runs without errors (`python validate_scripts.py`)
- [ ] README.md includes all required sections
- [ ] concept.svg is present and renders correctly (800x500, dark theme)
- [ ] Script works on multiple symbols and timeframes
- [ ] No hardcoded symbols, API keys, or external network calls
- [ ] Entry added to index.json
- [ ] Does not duplicate a built-in indicator or existing marketplace script

## License

By contributing, you agree that your contribution will be licensed under the Apache 2.0 license.

## Trademarks

Pine Script is a registered trademark of TradingView, Inc. TradeGrub is not affiliated with, endorsed by, or sponsored by TradingView. References to "Pine-compatible" describe interoperability with the Pine Script language and do not imply any association with TradingView.
