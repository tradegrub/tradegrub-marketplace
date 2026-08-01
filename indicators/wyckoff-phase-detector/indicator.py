from tg_scripting import *

lookback = input.int(50, "Lookback Period", minval=10, maxval=200)
vol_ma_len = input.int(20, "Volume MA Length", minval=5, maxval=100)
spring_threshold = input.float(0.02, "Spring/Upthrust Threshold")

support = ta.lowest(low, lookback)
resistance = ta.highest(high, lookback)
range_size = resistance - support

vol_ma = ta.sma(volume, vol_ma_len)
vol_ratio = volume / vol_ma

range_pos = (close - support) / range_size

spring_level = support * (1 - spring_threshold)
upthrust_level = resistance * (1 + spring_threshold)

spring_sig = (low < spring_level) & (close > support) & (vol_ratio > 1.5)
upthrust_sig = (high > upthrust_level) & (close < resistance) & (vol_ratio > 1.5)

is_up = close > open
is_dn = close < open

up_vol = volume * is_up
down_vol = volume * is_dn

avg_up_vol = ta.sma(up_vol, vol_ma_len)
avg_down_vol = ta.sma(down_vol, vol_ma_len)

vol_score = (avg_up_vol - avg_down_vol) / vol_ma * 100

phase_score = vol_score + spring_sig * 30 - upthrust_sig * 30

phase_score[phase_score > 100] = 100
phase_score[phase_score < -100] = -100

smooth_score = ta.sma(phase_score, 5)

plot(smooth_score, title="Wyckoff Phase Score", color="#FFD700")
hline(0, title="Neutral", color="#555555")
hline(50, title="Strong Accumulation", color="#00AA00")
hline(-50, title="Strong Distribution", color="#AA0000")

bgcolor(smooth_score > 20, color="rgba(0, 200, 100, 0.08)")
bgcolor(smooth_score < -20, color="rgba(200, 50, 50, 0.08)")

plotshape(spring_sig, title="Spring", style="triangleup", location="belowbar", color="#00FF88")
plotshape(upthrust_sig, title="Upthrust", style="triangledown", location="abovebar", color="#FF4444")
