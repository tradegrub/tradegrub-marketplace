from tg_scripting import *
import numpy as np

indicator("Markov Regime Strategy", overlay=True)

ret_len = input.int(10, "Return Length", minval=2, maxval=50)
threshold = input.float(0.5, "State Threshold %", minval=0.1, maxval=5.0)
window = input.int(50, "Rolling Window", minval=20, maxval=200)
entry_prob = input.float(0.6, "Entry Probability", minval=0.5, maxval=0.95)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_stop = input.float(2.0, "ATR Stop Multiple", minval=1.0, maxval=5.0)
tp_ratio = input.float(2.0, "Take Profit Ratio", minval=1.0, maxval=5.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

atr = ta.atr(high, low, close, atr_len)
n = len(close)

# Compute returns and discretize into states: 0=bear, 1=neutral, 2=bull
returns = np.zeros(n)
for i in range(ret_len, n):
    returns[i] = (float(close[i]) - float(close[i - ret_len])) / float(close[i - ret_len]) * 100

states = np.ones(n, dtype=int)  # default neutral
thresh = threshold
for i in range(n):
    if returns[i] > thresh:
        states[i] = 2  # bull
    elif returns[i] < -thresh:
        states[i] = 0  # bear

# Compute rolling transition matrix and regime probabilities
bull_prob = np.zeros(n)
bear_prob = np.zeros(n)
neutral_prob = np.zeros(n)

for i in range(window + 1, n):
    # Build transition count matrix from rolling window
    trans = np.zeros((3, 3))
    for j in range(i - window, i):
        trans[states[j - 1], states[j]] += 1

    # Normalize rows to get transition probabilities
    row_sums = trans.sum(axis=1)
    prob_matrix = np.zeros((3, 3))
    for r in range(3):
        if row_sums[r] > 0:
            prob_matrix[r] = trans[r] / row_sums[r]

    # Current state -> next state probabilities
    cur = states[i]
    bear_prob[i] = prob_matrix[cur, 0]
    neutral_prob[i] = prob_matrix[cur, 1]
    bull_prob[i] = prob_matrix[cur, 2]

# Generate signals
long_signal = np.zeros(n, dtype=bool)
short_signal = np.zeros(n, dtype=bool)

for i in range(window + 2, n):
    if bull_prob[i] >= entry_prob and bull_prob[i - 1] < entry_prob:
        long_signal[i] = True
    if bear_prob[i] >= entry_prob and bear_prob[i - 1] < entry_prob:
        short_signal[i] = True

# Strategy execution with ATR stops
in_long = False
in_short = False
entry_price_tracked = 0.0

for i in range(n):
    strategy.set_bar_index(i)
    if long_signal[i] and not in_long:
        strategy.entry("Long", strategy.LONG)
        in_long = True
        in_short = False
        entry_price_tracked = float(close[i])
    elif short_signal[i] and not in_short:
        strategy.entry("Short", strategy.SHORT)
        in_short = True
        in_long = False
        entry_price_tracked = float(close[i])

    if in_long:
        sl = entry_price_tracked - float(atr[i]) * atr_stop
        tp = entry_price_tracked + float(atr[i]) * atr_stop * tp_ratio
        strategy.exit("Long", stop=sl, limit=tp)
        if float(close[i]) <= sl or float(close[i]) >= tp:
            in_long = False
        # Exit on rising bear probability
        if bear_prob[i] >= entry_prob:
            strategy.exit("Long")
            in_long = False

    if in_short:
        sl = entry_price_tracked + float(atr[i]) * atr_stop
        tp = entry_price_tracked - float(atr[i]) * atr_stop * tp_ratio
        strategy.exit("Short", stop=sl, limit=tp)
        if float(close[i]) >= sl or float(close[i]) <= tp:
            in_short = False
        if bull_prob[i] >= entry_prob:
            strategy.exit("Short")
            in_short = False

# Background coloring for regime zones
bgcolor_vals = [
    (
        "rgba(0,230,118,0.12)" if (i > window and bull_prob[i] >= 0.5)
        else "rgba(255,23,68,0.12)" if (i > window and bear_prob[i] >= 0.5)
        else "rgba(66,165,245,0.10)" if i > window
        else None
    )
    for i in range(n)
]
bgcolor(bgcolor_vals)

# Entry threshold reference line
hline(entry_prob, title="Entry Threshold", color="#ffc107")
hline(0.5, title="50% Regime Line", color="gray")

# Plot signals
plotshape(long_signal, title="Long Entry", style="triangleup", location="belowbar", color="#00e676")
plotshape(short_signal, title="Short Entry", style="triangledown", location="abovebar", color="#ff1744")

# Regime probability lines
plot(bull_prob, title="Bull Probability", color="#00e676")
plot(bear_prob, title="Bear Probability", color="#ff1744")
plot(neutral_prob, title="Neutral Probability", color="#42a5f5")

# Labels and level annotations
last_long_ann = -100
last_short_ann = -100
cooldown = 20
ann_bars = 25

for i in range(n):
    if long_signal[i] and (i - last_long_ann) > cooldown:
        last_long_ann = i
        if show_labels:
            prob_text = "BULL REGIME\nP={:.0f}%".format(bull_prob[i] * 100)
            label.new(x=i, y=float(low[i]), text=prob_text,
                      style=label.style_label_up, color="#00e676",
                      textcolor="#000000", size="normal")
        if show_levels:
            ep = float(close[i])
            sl = ep - float(atr[i]) * atr_stop
            tp = ep + float(atr[i]) * atr_stop * tp_ratio
            end = min(i + ann_bars, n - 1)
            line.new(x1=i, y1=ep, x2=end, y2=ep,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=ep, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl, x2=end, y2=sl,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp, x2=end, y2=tp,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=tp, right=end, bottom=sl,
                    border_color="rgba(66,165,245,0.15)", bgcolor="rgba(66,165,245,0.03)")

    if short_signal[i] and (i - last_short_ann) > cooldown:
        last_short_ann = i
        if show_labels:
            prob_text = "BEAR REGIME\nP={:.0f}%".format(bear_prob[i] * 100)
            label.new(x=i, y=float(high[i]), text=prob_text,
                      style=label.style_label_down, color="#ff1744",
                      textcolor="#ffffff", size="normal")
        if show_levels:
            ep = float(close[i])
            sl = ep + float(atr[i]) * atr_stop
            tp = ep - float(atr[i]) * atr_stop * tp_ratio
            end = min(i + ann_bars, n - 1)
            line.new(x1=i, y1=ep, x2=end, y2=ep,
                     color="#42a5f5", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=ep, text="Entry",
                      style=label.style_label_left, color="rgba(66,165,245,0.2)",
                      textcolor="#42a5f5", size="small")
            line.new(x1=i, y1=sl, x2=end, y2=sl,
                     color="#ef5350", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=sl, text="Stop Loss",
                      style=label.style_label_left, color="rgba(239,83,80,0.2)",
                      textcolor="#ef5350", size="small")
            line.new(x1=i, y1=tp, x2=end, y2=tp,
                     color="#00e676", width=1, style=line.style_dashed)
            label.new(x=i + 2, y=tp, text="Take Profit",
                      style=label.style_label_left, color="rgba(0,230,118,0.2)",
                      textcolor="#00e676", size="small")
            box.new(left=i, top=sl, right=end, bottom=tp,
                    border_color="rgba(239,83,80,0.15)", bgcolor="rgba(239,83,80,0.03)")

# State transition labels
last_state_ann = -100
prev_state = 1
for i in range(window + 1, n):
    cur = states[i]
    if cur != prev_state and (i - last_state_ann) > cooldown and show_labels:
        last_state_ann = i
        names = ["Bear", "Neutral", "Bull"]
        label.new(x=i, y=float(close[i]), text=names[cur],
                  style=label.style_label_center, color="rgba(255,255,255,0.1)",
                  textcolor="#aaaaaa", size="tiny")
    prev_state = cur
