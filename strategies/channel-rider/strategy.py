from tg_scripting import *
import numpy as np

indicator("Channel Rider", overlay=True)

length = input.int(50, "Regression Length", minval=10, maxval=200)
mult = input.float(2.0, "Channel Width", minval=0.5, maxval=4.0)
trend_len = input.int(100, "Trend EMA Length", minval=20, maxval=300)
atr_len = input.int(14, "ATR Length", minval=5, maxval=50)
atr_sl_mult = input.float(1.5, "ATR Stop-Loss Mult", minval=0.5, maxval=4.0)
atr_tp_mult = input.float(2.5, "ATR Take-Profit Mult", minval=1.0, maxval=6.0)
require_trend = input.bool(True, "Require Trend Alignment")
rsi_filter = input.bool(True, "RSI Confirmation")
show_labels = input.bool(True, "Show Labels")
show_levels = input.bool(True, "Show Entry/Stop/TP Levels")

mid = ta.linreg(close, length)
dev = ta.stdev(close, length) * mult
upper = mid + dev
lower = mid - dev

trend_ema = ta.ema(close, trend_len)
atr = ta.atr(high, low, close, atr_len)
rsi = ta.rsi(close, 14)

uptrend = close > trend_ema
downtrend = close < trend_ema

long_signal = (close <= lower) & (~require_trend | uptrend) & (~rsi_filter | (rsi < 35))
short_signal = (close >= upper) & (~require_trend | downtrend) & (~rsi_filter | (rsi > 65))

plot(mid, color="white", title="Midline")
plot(upper, color="red", title="Upper Band")
plot(lower, color="green", title="Lower Band")
plot(trend_ema, color="orange", linewidth=1, title="Trend EMA")
bgcolor(long_signal, color="rgba(0,255,0,0.08)")
bgcolor(short_signal, color="rgba(255,0,0,0.08)")

n = len(close)
last_signal_idx = -100
cooldown = 20
exit_bars = 30
channel_label_placed = False

for i in range(length, n):
    if long_signal[i]:
        sl = close[i] - atr[i] * atr_sl_mult
        tp = close[i] + atr[i] * atr_tp_mult
        strategy.entry("Long", strategy.LONG, stop_loss=sl, take_profit=tp)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(low[i]), text="LONG\nChannel Low",
                          style=label.style_label_up, color="#00e676",
                          textcolor="#000000", size="normal")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(sl)
                tp_price = float(tp)
                end_bar = min(i + exit_bars, n - 1)
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

    elif short_signal[i]:
        sl = close[i] + atr[i] * atr_sl_mult
        tp = close[i] - atr[i] * atr_tp_mult
        strategy.entry("Short", strategy.SHORT, stop_loss=sl, take_profit=tp)

        if (i - last_signal_idx) > cooldown:
            last_signal_idx = i
            if show_labels:
                label.new(x=i, y=float(high[i]), text="SHORT\nChannel High",
                          style=label.style_label_down, color="#ef5350",
                          textcolor="#ffffff", size="normal")
            if show_levels:
                entry_price = float(close[i])
                sl_price = float(sl)
                tp_price = float(tp)
                end_bar = min(i + exit_bars, n - 1)
                line.new(x1=i, y1=entry_price, x2=end_bar, y2=entry_price,
                         color="#42a5f5", width=1, style=line.style_dashed)
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

    # Label the channel once
    if show_labels and not channel_label_placed:
        channel_label_placed = True
        label.new(x=i, y=float(upper[i]), text="Regression Channel",
                  style=label.style_label_down, color="rgba(136,136,136,0.3)",
                  textcolor="#888888", size="normal")

    if strategy.position_size > 0 and close[i] >= mid[i]:
        strategy.close("Long")
    elif strategy.position_size < 0 and close[i] <= mid[i]:
        strategy.close("Short")
