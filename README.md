# TradeGrub Marketplace

Community marketplace for TradeGrub Charts strategies and indicators. Browse, share, and install free trading strategies and indicators with built-in backtesting and issue tracking.

## Folder Structure

```text
tradegrub-marketplace/
  manifest.schema.json        # JSON Schema for manifest validation
  CONTRIBUTING.md              # How to add strategies
  strategies/                  # Pine-compatible + Python strategies
  indicators/                  # Pine-compatible + Python indicators
  .github/ISSUE_TEMPLATE/      # Bug reports, features, submissions
```

Each script folder contains:

- `manifest.json` -- metadata, version, category, tags
- `strategy.py` or `indicator.py` -- Python script using the `tg_scripting` API
- `README.md` -- documentation, parameters, signals
- `concept.svg` -- visual diagram of the strategy or indicator concept

## Supported Languages

Scripts can be written in:

- **Pine-compatible** -- runs on the built-in Pine-compatible interpreter
- **Python** -- available packages: numpy, pandas, scipy, scikit-learn, matplotlib, lightgbm, xgboost

## Issues and Discussions

Every strategy and indicator has its own issue and discussion space on GitHub.

**Report a bug or request a feature:** Use [GitHub Issues](../../issues) with a label matching the script name. For example, to report a bug with the MA Crossover strategy, create an issue and add the `ma-crossover` label.

To filter issues for a specific script:

- `label:ma-crossover` -- all issues for MA Crossover
- `label:regime-detector` -- all issues for Market Regime Detector
- `label:bug label:bollinger-bands` -- bugs for Bollinger Bands

**Community discussions:** Use [GitHub Discussions](../../discussions) to ask questions, share setups, post backtest results, or suggest parameter tweaks for any strategy or indicator. Each discussion category maps to a script type:

- **Strategies** -- discussion about strategy logic, parameter tuning, and backtest results
- **Indicators** -- discussion about indicator behavior, interpretation, and use cases
- **General** -- marketplace-wide topics, feature ideas, and community announcements

## Install a Script

Copy the script contents into the TradeGrub script editor, or install directly from the in-app marketplace at [tradegrub.finance](https://tradegrub.finance).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on adding your own strategies and indicators.

## License

Apache 2.0. See [LICENSE](LICENSE) for details.

## Strategies

| Strategy | Concept | Description |
| -------- | ------- | ----------- |
| [MA Crossover](strategies/ma-crossover/) | <img src="strategies/ma-crossover/concept.svg" width="400"> | Classic moving average crossover with configurable fast/slow periods |
| [Bollinger Bands](strategies/bollinger-bands/) | <img src="strategies/bollinger-bands/concept.svg" width="400"> | Bollinger Band squeeze breakout with volume confirmation |
| [RSI Mean Reversion](strategies/rsi-mean-reversion/) | <img src="strategies/rsi-mean-reversion/concept.svg" width="400"> | Mean reversion entries on RSI extremes with ATR stops |
| [Supertrend](strategies/supertrend/) | <img src="strategies/supertrend/concept.svg" width="400"> | Supertrend trend-following with trailing stop |
| [MACD Crossover](strategies/macd-crossover/) | <img src="strategies/macd-crossover/concept.svg" width="400"> | MACD signal line crossover with histogram confirmation |
| [EMA Crossover](strategies/ema-crossover/) | <img src="strategies/ema-crossover/concept.svg" width="400"> | Exponential moving average crossover strategy |
| [Ichimoku Cloud](strategies/ichimoku-cloud/) | <img src="strategies/ichimoku-cloud/concept.svg" width="400"> | Ichimoku cloud breakout with Tenkan/Kijun cross |
| [ATR Breakout](strategies/atr-breakout/) | <img src="strategies/atr-breakout/concept.svg" width="400"> | Volatility breakout using ATR expansion |
| [Donchian Breakout](strategies/donchian-breakout/) | <img src="strategies/donchian-breakout/concept.svg" width="400"> | Donchian channel breakout with trend filter |
| [Descending Channel Break](strategies/descending-channel-break/) | <img src="strategies/descending-channel-break/concept.svg" width="400"> | Descending channel breakout with volume surge |
| [Savitzky-Golay Peak Reversal](strategies/peak-reversal/) | <img src="strategies/peak-reversal/concept.svg" width="400"> | Signal processing to detect peak/trough reversals |
| [Grid Level Trader](strategies/grid-trader/) | <img src="strategies/grid-trader/concept.svg" width="400"> | Grid trading that buys at lower price levels and sells at upper levels |
| [Safety Order DCA](strategies/dca-safety-orders/) | <img src="strategies/dca-safety-orders/concept.svg" width="400"> | Dollar cost averaging with safety orders at progressively lower prices |
| [Pyramid Accumulator](strategies/pyramid-accumulator/) | <img src="strategies/pyramid-accumulator/concept.svg" width="400"> | Systematic accumulation on dips with profit target exit |
| [RMI Band Reversal](strategies/rmi-band-reversal/) | <img src="strategies/rmi-band-reversal/concept.svg" width="400"> | Relative Momentum Index with Bollinger Bands for mean reversion |
| [Band Trend Breakout](strategies/band-trend-breakout/) | <img src="strategies/band-trend-breakout/concept.svg" width="400"> | Adaptive EMA-ATR band breakout with center line trailing |
| [Martingale Grid](strategies/martingale-grid/) | <img src="strategies/martingale-grid/concept.svg" width="400"> | Grid trading with martingale position sizing and average entry take profit |

**[Browse all strategies →](strategies/)**

## Indicators

| Indicator | Concept | Description |
| --------- | ------- | ----------- |
| [Market Regime Detector](indicators/regime-detector/) | <img src="indicators/regime-detector/concept.svg" width="400"> | KMeans clustering on ATR%, returns, and volume to classify market regimes |
| [Price Distribution Analysis](indicators/price-distribution/) | <img src="indicators/price-distribution/concept.svg" width="400"> | Rolling z-score, percentile rank, and probability density for extreme levels |
| [Fourier Cycle Analysis](indicators/fourier-cycles/) | <img src="indicators/fourier-cycles/concept.svg" width="400"> | FFT decomposition to identify dominant price cycles and filtered reconstruction |
| [Volume Profile POC](indicators/volume-profile-poc/) | <img src="indicators/volume-profile-poc/concept.svg" width="400"> | Volume profile with point of control and value area |
| [VWAP StdDev Bands](indicators/vwap-stddev-bands/) | <img src="indicators/vwap-stddev-bands/concept.svg" width="400"> | VWAP with standard deviation bands |
| [Smart Money Concepts](indicators/smart-money-concepts/) | <img src="indicators/smart-money-concepts/concept.svg" width="400"> | Order blocks, fair value gaps, and liquidity sweeps |
| [Supply Demand Zones](indicators/supply-demand-zones/) | <img src="indicators/supply-demand-zones/concept.svg" width="400"> | Automatic supply and demand zone detection |
| [EMA Ribbon](indicators/ema-ribbon/) | <img src="indicators/ema-ribbon/concept.svg" width="400"> | Multi-period EMA ribbon for trend visualization |
| [Kalman Filter Trend](indicators/kalman-filter-trend/) | <img src="indicators/kalman-filter-trend/concept.svg" width="400"> | Kalman filter smoothed trend with noise reduction |
| [Volume Divergence Scanner](indicators/volume-divergence-scanner/) | <img src="indicators/volume-divergence-scanner/concept.svg" width="400"> | Swing point analysis to detect price-volume divergences |
| [Pivot Fakeout Filter](indicators/pivot-fakeout-filter/) | <img src="indicators/pivot-fakeout-filter/concept.svg" width="400"> | Pivot points with tolerance bands to filter false breakouts |
| [Auto Price Grid](indicators/auto-price-grid/) | <img src="indicators/auto-price-grid/concept.svg" width="400"> | Automatic horizontal grid from high to low with zone highlighting |
| [MA Deviation Channel](indicators/ma-deviation-channel/) | <img src="indicators/ma-deviation-channel/concept.svg" width="400"> | Dynamic channels based on historical percentage deviation from a moving average |
| [Three Candle Sweep](indicators/three-candle-sweep/) | <img src="indicators/three-candle-sweep/concept.svg" width="400"> | Three-candle liquidity sweep pattern detection for price action reversals |
| [Daily Percent Levels](indicators/daily-percent-levels/) | <img src="indicators/daily-percent-levels/concept.svg" width="400"> | Horizontal price levels at fixed percentage intervals from a reference price |
| [Auto Anchor VWAP](indicators/auto-anchor-vwap/) | <img src="indicators/auto-anchor-vwap/concept.svg" width="400"> | Three simultaneous VWAPs with auto-detected anchors from trend highs and lows |
| [Normalized Volume Volatility](indicators/normalized-volume-volatility/) | <img src="indicators/normalized-volume-volatility/concept.svg" width="400"> | Volume and volatility normalized against statistical baselines with regression |
| [Double Bollinger Bands](indicators/double-bollinger-bands/) | <img src="indicators/double-bollinger-bands/concept.svg" width="400"> | Two sets of Bollinger Bands at 1σ and 2σ for volatility zone identification |
| [ATR Range Levels](indicators/atr-range-levels/) | <img src="indicators/atr-range-levels/concept.svg" width="400"> | Projected daily price range using ATR with intermediate levels |
| [Multi Period Opens](indicators/multi-period-opens/) | <img src="indicators/multi-period-opens/concept.svg" width="400"> | Daily, weekly, monthly, and yearly opening price reference levels |
| [Bar Behavior Analysis](indicators/bar-behavior-analysis/) | <img src="indicators/bar-behavior-analysis/concept.svg" width="400"> | Statistical odds of bullish or bearish follow-through on subsequent bars |
| [Inside Bar Failure](indicators/inside-bar-failure/) | <img src="indicators/inside-bar-failure/concept.svg" width="400"> | Inside bar breakout failure detection for reversal signals |
| [Momentum Confirmed Pivots](indicators/momentum-confirmed-pivots/) | <img src="indicators/momentum-confirmed-pivots/concept.svg" width="400"> | Pivot highs and lows filtered by RSI momentum confirmation |
| [Multi-Oscillator Divergence](indicators/multi-oscillator-divergence/) | <img src="indicators/multi-oscillator-divergence/concept.svg" width="400"> | Aggregated divergence across RSI, MACD, and Stochastic for high-confidence signals |
| [Volatility Extreme Detector](indicators/volatility-extreme-detector/) | <img src="indicators/volatility-extreme-detector/concept.svg" width="400"> | Synthetic volatility measure detecting extreme bottoms and tops |
| [Candlestick Sentiment Score](indicators/candlestick-sentiment-score/) | <img src="indicators/candlestick-sentiment-score/concept.svg" width="400"> | Composite bar sentiment from body direction, close position, and wick bias |
| [Supertrend Fakeout Filter](indicators/supertrend-fakeout-filter/) | <img src="indicators/supertrend-fakeout-filter/concept.svg" width="400"> | Supertrend with post-flip distance validation to filter false reversals |
| [Combined Candle Merge](indicators/combined-candle-merge/) | <img src="indicators/combined-candle-merge/concept.svg" width="400"> | Merges consecutive same-direction candles into single aggregate bars |
| [Quasimodo Reversal](indicators/quasimodo-reversal/) | <img src="indicators/quasimodo-reversal/concept.svg" width="400"> | Detects Quasimodo reversal patterns from asymmetric swing structure |
| [Volumetric Candle Intensity](indicators/volumetric-candle-intensity/) | <img src="indicators/volumetric-candle-intensity/concept.svg" width="400"> | Volume normalized by standard deviation with directional intensity coloring |
| [Supertrend Fibonacci Levels](indicators/supertrend-fibonacci-levels/) | <img src="indicators/supertrend-fibonacci-levels/concept.svg" width="400"> | Supertrend with automatic Fibonacci retracement from each trend swing |
| [Harmonic Pattern Scanner](indicators/harmonic-pattern-scanner/) | <img src="indicators/harmonic-pattern-scanner/concept.svg" width="400"> | Detects Gartley, Butterfly, Bat, and Crab patterns using zigzag swing structure |
| [Sentiment Mood Oscillator](indicators/sentiment-mood-oscillator/) | <img src="indicators/sentiment-mood-oscillator/concept.svg" width="400"> | Multi-layered sentiment oscillator combining RSI, MFI, and momentum into a mood score |
| [HalfTrend Indicator](indicators/halftrend-indicator/) | <img src="indicators/halftrend-indicator/concept.svg" width="400"> | ATR-based trend indicator using channel midpoint logic with directional flip signals |
| [Volatility Contraction Pattern](indicators/volatility-contraction-pattern/) | <img src="indicators/volatility-contraction-pattern/concept.svg" width="400"> | Detects progressively tighter price ranges with declining volume for breakout setups |
| [Wyckoff Phase Detector](indicators/wyckoff-phase-detector/) | <img src="indicators/wyckoff-phase-detector/concept.svg" width="400"> | Detects Wyckoff accumulation and distribution phases using volume patterns |
| [Central Pivot Range](indicators/central-pivot-range/) | <img src="indicators/central-pivot-range/concept.svg" width="400"> | CPR with TC/BC levels, narrow CPR breakout detection |
| [Gann Square Levels](indicators/gann-square-levels/) | <img src="indicators/gann-square-levels/concept.svg" width="400"> | Gann Square of Nine price levels from significant highs and lows |
| [Fibonacci Confluence Mapper](indicators/fibonacci-confluence-mapper/) | <img src="indicators/fibonacci-confluence-mapper/concept.svg" width="400"> | Finds where multiple Fibonacci retracement levels cluster together |
| [Rounding Bottom Scanner](indicators/rounding-bottom-scanner/) | <img src="indicators/rounding-bottom-scanner/concept.svg" width="400"> | Detects rounding bottom patterns using curvature and volume analysis |
| [Stair-Step Trend Detector](indicators/stairstep-trend-detector/) | <img src="indicators/stairstep-trend-detector/concept.svg" width="400"> | Detects orderly stair-step trending with consistent step sizes |
| [Consecutive Candle Streak](indicators/consecutive-candle-streak/) | <img src="indicators/consecutive-candle-streak/concept.svg" width="400"> | Tracks candle streaks and identifies exhaustion points |
| [Nadaraya-Watson Envelope](indicators/nadaraya-watson-envelope/) | <img src="indicators/nadaraya-watson-envelope/concept.svg" width="400"> | Kernel regression price channel with ATR envelopes |
| [Swing Failure Pattern](indicators/swing-failure-pattern/) | <img src="indicators/swing-failure-pattern/concept.svg" width="400"> | Detects liquidity grab reversals at swing levels |
| [Monotonicity Index](indicators/monotonicity-index/) | <img src="indicators/monotonicity-index/concept.svg" width="400"> | Measures trend consistency and orderliness |
| [Unreached Highs/Lows](indicators/unreached-highs-lows/) | <img src="indicators/unreached-highs-lows/concept.svg" width="400"> | Gauges trend persistence via unrevisited price levels |
| [Volume Surprise Detector](indicators/volume-surprise-detector/) | <img src="indicators/volume-surprise-detector/concept.svg" width="400"> | Z-score volume anomaly detection |
| [Probabilistic Breakout Forecast](indicators/probabilistic-breakout-forecast/) | <img src="indicators/probabilistic-breakout-forecast/concept.svg" width="400"> | Statistical breakout probability from range compression |
| [Market Criticality Index](indicators/self-organized-criticality/) | <img src="indicators/self-organized-criticality/concept.svg" width="400"> | Market fragility index combining tail risk, volatility clustering, and range compression into a 0-100 criticality score |
| [First Passage Time Estimator](indicators/first-passage-time/) | <img src="indicators/first-passage-time/concept.svg" width="400"> | Estimates probability of price reaching upper and lower target levels using geometric Brownian motion first passage analysis |
| [Fractal Dimension Index](indicators/fractal-dimension-index/) | <img src="indicators/fractal-dimension-index/concept.svg" width="400"> | Chaos theory metric using rescaled range analysis to determine if price is trending, random, or mean-reverting |
| [Mean Reversion Detector](indicators/adf-stationarity-test/) | <img src="indicators/adf-stationarity-test/concept.svg" width="400"> | Rolling Augmented Dickey-Fuller test to detect mean-reverting price behavior using least squares regression |
| [Markov Regime Oscillator](indicators/markov-regime-model/) | <img src="indicators/markov-regime-model/concept.svg" width="400"> | Two-state Markov chain classifying bars as trending or ranging with rolling transition probability estimation |
| [Andean Oscillator](indicators/andean-oscillator/) | <img src="indicators/andean-oscillator/concept.svg" width="400"> | Exponential envelope oscillator with bull and bear decomposition |
| [LOWESS Trend](indicators/lowess-trend/) | <img src="indicators/lowess-trend/concept.svg" width="400"> | Locally weighted scatterplot smoothing trend line with breakout detection |
| [Logarithmic Moving Average](indicators/log-moving-average/) | <img src="indicators/log-moving-average/concept.svg" width="400"> | Moving average with logarithmic weighting and signal line crossovers |
| [Trend Volatility Index](indicators/trend-volatility-index/) | <img src="indicators/trend-volatility-index/concept.svg" width="400"> | Gini mean difference of multiple SMAs normalized to measure trend strength vs consolidation |
| [Detrended Rhythm Oscillator](indicators/detrended-rhythm-oscillator/) | <img src="indicators/detrended-rhythm-oscillator/concept.svg" width="400"> | Detrends price with SMA removal and finds dominant cycle via autocorrelation |
| [Cybernetic Oscillator](indicators/cybernetic-oscillator/) | <img src="indicators/cybernetic-oscillator/concept.svg" width="400"> | Bandpass filter oscillator using cascaded highpass and lowpass EMA filtering |
| [MA Entanglement Index](indicators/ma-entanglement/) | <img src="indicators/ma-entanglement/concept.svg" width="400"> | Measures how tangled 6 moving averages are to detect consolidation vs trending |
| [Range Filter](indicators/range-filter/) | <img src="indicators/range-filter/concept.svg" width="400"> | Volatility-adaptive stepped trend filter that only moves when price exceeds the filter by a smoothed ATR range |
| [Entropy Risk Measure](indicators/evar-risk-measure/) | <img src="indicators/evar-risk-measure/concept.svg" width="400"> | Entropy-adjusted Value at Risk using Cornish-Fisher expansion with position sizing |
| [Stop Loss Cascade Detector](indicators/stop-loss-cascade/) | <img src="indicators/stop-loss-cascade/concept.svg" width="400"> | Detects where stop losses cluster near swing levels and models cascade breakout potential |
| [Effort vs Results Oscillator](indicators/effort-vs-results/) | <img src="indicators/effort-vs-results/concept.svg" width="400"> | Wyckoff effort-result principle measuring volume effort against price movement results |
| [Statistical Bin S/R](indicators/bin-support-resistance/) | <img src="indicators/bin-support-resistance/concept.svg" width="400"> | Finds support and resistance levels by grouping price action into statistical bins |
| [Congestion Index](indicators/congestion-index/) | <img src="indicators/congestion-index/concept.svg" width="400"> | Measures consolidation intensity by comparing N-bar range to sum of individual bar ranges |
| [Bar Shape Oscillator](indicators/bar-shape-oscillator/) | <img src="indicators/bar-shape-oscillator/concept.svg" width="400"> | Amplitude-free directional oscillator derived purely from candlestick bar shape ratios |
| [Volatility Estimator Suite](indicators/volatility-estimator-suite/) | <img src="indicators/volatility-estimator-suite/concept.svg" width="400"> | Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang range-based volatility estimators |
| [Hurst Cycle Pivots](indicators/hurst-cycle-pivots/) | <img src="indicators/hurst-cycle-pivots/concept.svg" width="400"> | Rolling Hurst exponent via R/S analysis for trending vs mean-reverting regime detection |
| [Linear Predictive Filter](indicators/linear-predictive-filter/) | <img src="indicators/linear-predictive-filter/concept.svg" width="400"> | LPC via Yule-Walker equations to extract dominant cycles and predict next price value |
| [Trend Template Qualifier](indicators/minervini-qualifier/) | <img src="indicators/minervini-qualifier/concept.svg" width="400"> | Scores stocks 0-6 against stage-2 trend template conditions |
| [Smoothed Price Candles](indicators/berlin-candles/) | <img src="indicators/berlin-candles/concept.svg" width="400"> | EMA-smoothed OHLC candles that preserve actual close prices and high/low extremes |
| [MESA Adaptive Stochastic](indicators/mesa-stochastic/) | <img src="indicators/mesa-stochastic/concept.svg" width="400"> | Stochastic oscillator with adaptive period from autocorrelation cycle detection |
| [Optimized Trend Tracker](indicators/optimized-trend-tracker/) | <img src="indicators/optimized-trend-tracker/concept.svg" width="400"> | Percentage-based optimized trailing trend tracker using EMA with adaptive bands |
| [Phase Loop Oscillator](indicators/ehlers-phase-loop/) | <img src="indicators/ehlers-phase-loop/concept.svg" width="400"> | Price-volume quadrant analysis for detecting accumulation and distribution phases |
| [WaveTrend Enhanced](indicators/wavetrend-enhanced/) | <img src="indicators/wavetrend-enhanced/concept.svg" width="400"> | Enhanced WaveTrend with channel index smoothing and automated divergence detection |
| [Distance Classifier](indicators/lorentzian-classifier/) | <img src="indicators/lorentzian-classifier/concept.svg" width="400"> | KNN classifier using Lorentzian distance across RSI, CCI, ROC, and volatility features |
| [Candlestick Pattern Score](indicators/adaptive-candlestick-score/) | <img src="indicators/adaptive-candlestick-score/concept.svg" width="400"> | Composite candlestick pattern score weighted by historical success rate |
| [Absorption Detector](indicators/absorption-detector/) | <img src="indicators/absorption-detector/concept.svg" width="400"> | Detects where large passive orders absorbed aggressive flow |
| [Bar Efficiency Ratio](indicators/bar-efficiency-ratio/) | <img src="indicators/bar-efficiency-ratio/concept.svg" width="400"> | Measures price movement efficiency within each bar as body to range ratio |
| [Time at Price Levels](indicators/time-at-price/) | <img src="indicators/time-at-price/concept.svg" width="400"> | Finds consolidation zones by counting bar dwell time per price level |
| [Movement Probability](indicators/gap-probability/) | <img src="indicators/gap-probability/concept.svg" width="400"> | Calculates next bar direction probability based on historical z-score patterns |
| [Probability Reversal Grid](indicators/probability-grid/) | <img src="indicators/probability-grid/concept.svg" width="400"> | Reversal probability based on position within recent range and historical zone behavior |
| [Arc Breakout Signals](indicators/d-shape-breakout/) | <img src="indicators/d-shape-breakout/concept.svg" width="400"> | Semi-circular arc-based support and resistance with curved breakout zones |
| [Causal Adaptive Smoother](indicators/causal-smoothing/) | <img src="indicators/causal-smoothing/concept.svg" width="400"> | Adaptive smoothing that reduces lag in calm markets and increases stability in volatile ones |
| [Momentum Rank](indicators/sector-momentum-rank/) | <img src="indicators/sector-momentum-rank/concept.svg" width="400"> | Weighted percentile composite of momentum across multiple timeframes |
| [Oscillator Channel Overlay](indicators/oscillator-channel-overlay/) | <img src="indicators/oscillator-channel-overlay/concept.svg" width="400"> | Maps RSI values into a regression channel on the price chart |
| [Sequential Exhaustion Counter](indicators/sequential-exhaustion/) | <img src="indicators/sequential-exhaustion/concept.svg" width="400"> | DeMark-style sequential counting system with setup and countdown phases |
| [Elliott Wave Counter](indicators/elliott-wave-counter/) | <img src="indicators/elliott-wave-counter/concept.svg" width="400"> | Automated Elliott Wave detection with 5-wave impulse pattern recognition |
| [Gap Closure Probability](indicators/gap-closure-stats/) | <img src="indicators/gap-closure-stats/concept.svg" width="400"> | Track price gap fill rates and display rolling closure probability |
| [Seasonal Pattern Projection](indicators/seasonal-projection/) | <img src="indicators/seasonal-projection/concept.svg" width="400"> | Average historical returns by cycle position to project seasonal direction |
| [Ease of Movement](indicators/ease-of-movement/) | <img src="indicators/ease-of-movement/concept.svg" width="400"> | Classic EMV measuring price movement efficiency relative to volume |
| [Spacetime Curvature Attractor](indicators/spacetime-attractor/) | <img src="indicators/spacetime-attractor/concept.svg" width="400"> | Physics-inspired mean reversion using volume mass and price acceleration |
| [Wave Phase Coherence](indicators/wave-phase-coherence/) | <img src="indicators/wave-phase-coherence/concept.svg" width="400"> | Constructive/destructive interference between RSI at three timeframes |
| [Impulse Decay Coefficient](indicators/impulse-decay/) | <img src="indicators/impulse-decay/concept.svg" width="400"> | Measures how much an impulse move has been absorbed by the pullback |
| [Skew Divergence Oscillator](indicators/skew-divergence/) | <img src="indicators/skew-divergence/concept.svg" width="400"> | Return skewness tracking with price-distribution divergence detection |
| [Tail Risk Oscillator](indicators/tail-risk-oscillator/) | <img src="indicators/tail-risk-oscillator/concept.svg" width="400"> | Excess kurtosis and skewness for elevated tail risk detection |
| [Dominant Cycle Length](indicators/dominant-cycle-length/) | <img src="indicators/dominant-cycle-length/concept.svg" width="400"> | Reports dominant cycle length and current phase via autocorrelation |
| [Composite Reversion Score](indicators/composite-reversion/) | <img src="indicators/composite-reversion/concept.svg" width="400"> | Blends momentum percentile, streak, and return percentile into reversion score |
| [Psychological Price Levels](indicators/psychological-levels/) | <img src="indicators/psychological-levels/concept.svg" width="400"> | Auto-drawn round number levels based on price magnitude |
| [Topographic Volume Nodes](indicators/topographic-volume-nodes/) | <img src="indicators/topographic-volume-nodes/concept.svg" width="400"> | Terrain prominence algorithm for high-volume price level detection |
| [Wick Asymmetry Ratio](indicators/wick-asymmetry/) | <img src="indicators/wick-asymmetry/concept.svg" width="400"> | Bounded oscillator measuring upper vs lower wick rejection pressure |
| [Candle Density Indicator](indicators/candle-density/) | <img src="indicators/candle-density/concept.svg" width="400"> | Candle body overlap density for congestion zone detection |
| [Kinetic Slippage Index](indicators/kinetic-slippage/) | <img src="indicators/kinetic-slippage/concept.svg" width="400"> | Gap between volume-implied and actual price movement |
| [Decennial Cycle Projection](indicators/round-trip-decay/) | <img src="indicators/round-trip-decay/concept.svg" width="400"> | Historical returns mapped by cycle position for seasonal projection |
| [Harmonic Adaptive Ribbon](indicators/harmonic-ribbon/) | <img src="indicators/harmonic-ribbon/concept.svg" width="400"> | Auto-tuned MA ribbon at harmonic multiples of detected dominant cycle |
| [Tilson T3 Moving Average](indicators/tilson-t3/) | <img src="indicators/tilson-t3/concept.svg" width="400"> | Six-stage ultra-smooth moving average with signal line |
| [Attention State Classifier](indicators/attention-classifier/) | <img src="indicators/attention-classifier/concept.svg" width="400"> | Transformer-style attention matching current state against historical patterns |
| [Projected Volume Estimate](indicators/projected-volume/) | <img src="indicators/projected-volume/concept.svg" width="400"> | Estimates projected final volume based on historical accumulation patterns |
| [Prime Cycle Timing](indicators/goldbach-timing/) | <img src="indicators/goldbach-timing/concept.svg" width="400"> | Prime number and Fibonacci cycle detection for reversal timing |
| [Liquidity Flow Proxy](indicators/m2-liquidity-proxy/) | <img src="indicators/m2-liquidity-proxy/concept.svg" width="400"> | Cumulative directional volume as a proxy for macro liquidity flow |

**[Browse all indicators →](indicators/)**
