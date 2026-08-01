from tg_scripting import *
import numpy as np

indicator("Multi Oscillator", overlay=True)

# Inputs
rsi_len = input.int(14, "RSI Length", minval=2, maxval=50)
cci_len = input.int(20, "CCI Length", minval=5, maxval=50)
stoch_len = input.int(14, "Stochastic Length", minval=2, maxval=50)
stoch_smooth = input.int(3, "Stochastic Smoothing", minval=1, maxval=10)
consensus = input.int(2, "Min Consensus (2 or 3)", minval=2, maxval=3)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

# Calculations
rsi = ta.rsi(close, rsi_len)
cci = ta.cci(close, cci_len)
stoch_k, _ = ta.stoch(high, low, close, stoch_len, 3, 3)
k_smooth = ta.sma(stoch_k, stoch_smooth)
atr = ta.atr(high, low, close, 14)

# Individual signals
rsi_bull = rsi > 50
rsi_bear = rsi < 50
cci_bull = cci > 0
cci_bear = cci < 0
stoch_bull = k_smooth > 50
stoch_bear = k_smooth < 50

# Consensus scoring
bull_score = rsi_bull.astype(int) + cci_bull.astype(int) + stoch_bull.astype(int)
bear_score = rsi_bear.astype(int) + cci_bear.astype(int) + stoch_bear.astype(int)

long_cond = bull_score >= consensus
short_cond = bear_score >= consensus

# Track previous state to only enter on new consensus
prev_long = np.roll(long_cond, 1)
prev_long[0] = False
prev_short = np.roll(short_cond, 1)
prev_short[0] = False

new_long = long_cond & ~prev_long
new_short = short_cond & ~prev_short

n = len(close)
last_signal_idx = -100
cooldown = 15

for i in range(len(close)):
    strategy.set_bar_index(i)
    if new_long[i]:
        strategy.entry("Long", strategy.LONG)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            score_val = int(bull_score[i])
            if show_labels:
                label.new(
                    x=i, y=float(low[i]),
                    text="LONG\n" + str(score_val) + "/3 Bull",
                    style=label.style_label_up,
                    color="#00e676",
                    textcolor="#000000",
                    size="normal"
                )
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(close[i] - atr[i] * 2.0)
                tp_price = float(close[i] + atr[i] * 4.0)
                end_bar = min(i + 30, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=entry_price, text="Entry",
                          style=label.style_label_left, color="rgba(66,165,245,0.2)",
                          textcolor="#42a5f5", size="small")
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=sl_price, text="Stop Loss",
                          style=label.style_label_left, color="rgba(239,83,80,0.2)",
                          textcolor="#ef5350", size="small")
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=tp_price, text="Take Profit",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=tp_price, right=end_bar, bottom=sl_price,
                        border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    elif new_short[i]:
        strategy.entry("Short", strategy.SHORT)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            score_val = int(bear_score[i])
            if show_labels:
                label.new(
                    x=i, y=float(high[i]),
                    text="SHORT\n" + str(score_val) + "/3 Bear",
                    style=label.style_label_down,
                    color="#ef5350",
                    textcolor="#ffffff",
                    size="normal"
                )
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(close[i] + atr[i] * 2.0)
                tp_price = float(close[i] - atr[i] * 4.0)
                end_bar = min(i + 30, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=entry_price, text="Entry",
                          style=label.style_label_left, color="rgba(66,165,245,0.2)",
                          textcolor="#42a5f5", size="small")
                line.new(x1=i, y1=sl_price, x2=end_bar, y2=sl_price,
                         color="#ef5350", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=sl_price, text="Stop Loss",
                          style=label.style_label_left, color="rgba(239,83,80,0.2)",
                          textcolor="#ef5350", size="small")
                line.new(x1=i, y1=tp_price, x2=end_bar, y2=tp_price,
                         color="#00e676", width=1, style=line.style_dashed)
                label.new(x=i + 2, y=tp_price, text="Take Profit",
                          style=label.style_label_left, color="rgba(0,230,118,0.2)",
                          textcolor="#00e676", size="small")
                box.new(left=i, top=sl_price, right=end_bar, bottom=tp_price,
                        border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

# Plots
plot(rsi, title="RSI", color="blue")
plot(cci / 4 + 50, title="CCI (scaled)", color="orange")
plot(k_smooth, title="Stochastic %K", color="purple")
hline(50, title="Midline", color="gray")

# --- Entry / exit markers ---
plotshape(new_long, title="Buy", style="triangleup", location="belowbar", color="green")
plotshape(new_short, title="Sell", style="triangledown", location="abovebar", color="red")
_exit_signal = (prev_long & ~long_cond) | (prev_short & ~short_cond)
plotshape(_exit_signal, title="Exit", style="xcross", location="abovebar", color="orange")

# --- Consensus zone backgrounds ---
bgcolor(long_cond, color="rgba(76,175,80,0.12)", title="Bullish Consensus")
bgcolor(short_cond, color="rgba(244,67,54,0.12)", title="Bearish Consensus")
