from tg_scripting import *
import numpy as np

indicator("Gap Recovery Play", overlay=True)

gap_pct = input.float(3.0, "Gap Down Threshold %", minval=1.0, maxval=10.0)
recovery_pct = input.float(50.0, "Recovery Fill %", minval=20.0, maxval=100.0)
sma_len = input.int(50, "Support SMA Length", minval=10, maxval=200)
rsi_len = input.int(14, "RSI Length", minval=5, maxval=30)
rsi_oversold = input.int(35, "RSI Oversold Level", minval=20, maxval=50)
atr_len = input.int(14, "ATR Length", minval=5, maxval=30)
atr_sl_mult = input.float(1.5, "ATR Stop Loss Multiple", minval=0.5, maxval=4.0)
atr_tp_mult = input.float(2.5, "ATR Take Profit Multiple", minval=1.0, maxval=6.0)
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

prev_close = np.concatenate([np.full(1, np.nan), (close)[:-1]])
sma_support = ta.sma(close, sma_len)
rsi = ta.rsi(close, rsi_len)
atr = ta.atr(high, low, close, atr_len)

gap_size = (prev_close - open) / prev_close * 100
gap_down = gap_size >= gap_pct

candle_range = high - low
candle_body = close - open
recovery_ratio = candle_body / candle_range * 100
strong_recovery = (candle_body > 0) & (recovery_ratio >= recovery_pct)

near_support = low <= sma_support * 1.02
rsi_ready = rsi <= rsi_oversold

entry_signal = gap_down & strong_recovery & near_support & rsi_ready

plot(sma_support, title="SMA Support", color="blue")
plot(rsi, title="RSI", color="purple", panel=1)
hline(rsi_oversold, title="Oversold", color="gray", panel=1)
plotshape(entry_signal, title="Gap Recovery", style="triangleup", location="belowbar", color="green")

n = len(close)
gap_bg_vals = [("rgba(244,67,54,0.12)" if gap_down[i] else None) for i in range(n)]
bgcolor(gap_bg_vals)

last_signal_idx = -100

for i in range(len(close)):
    strategy.set_bar_index(i)
    if entry_signal[i]:
        strategy.entry("Long", strategy.LONG)
        strategy.exit("Long", stop=close[i] - atr[i] * atr_sl_mult,
                       limit=close[i] + atr[i] * atr_tp_mult)

        if i - last_signal_idx >= 15:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(low[i]),
                          text="Gap Recovery\nLONG",
                          style=label.style_label_up,
                          color="#00e676", textcolor="#000000", size="normal")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(close[i] - atr[i] * atr_sl_mult)
                tp_price = float(close[i] + atr[i] * atr_tp_mult)
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
