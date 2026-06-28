from tg_scripting import *

colors = [
    "rgba(244,67,54,0.9)",
    "rgba(255,87,34,0.9)",
    "rgba(255,152,0,0.9)",
    "rgba(255,193,7,0.9)",
    "rgba(205,220,57,0.9)",
    "rgba(139,195,74,0.9)",
    "rgba(76,175,80,0.9)",
    "rgba(0,150,136,0.9)",
    "rgba(0,188,212,0.9)",
    "rgba(33,150,243,0.9)",
]

sma10 = ta.sma(close, 10)
sma20 = ta.sma(close, 20)
sma30 = ta.sma(close, 30)
sma40 = ta.sma(close, 40)
sma50 = ta.sma(close, 50)
sma60 = ta.sma(close, 60)
sma70 = ta.sma(close, 70)
sma80 = ta.sma(close, 80)
sma90 = ta.sma(close, 90)
sma100 = ta.sma(close, 100)

p1 = plot(sma10, title="SMA 10", color=colors[0])
p2 = plot(sma20, title="SMA 20", color=colors[1])
p3 = plot(sma30, title="SMA 30", color=colors[2])
p4 = plot(sma40, title="SMA 40", color=colors[3])
p5 = plot(sma50, title="SMA 50", color=colors[4])
p6 = plot(sma60, title="SMA 60", color=colors[5])
p7 = plot(sma70, title="SMA 70", color=colors[6])
p8 = plot(sma80, title="SMA 80", color=colors[7])
p9 = plot(sma90, title="SMA 90", color=colors[8])
p10 = plot(sma100, title="SMA 100", color=colors[9])

fill(p1, p2, color="rgba(244,67,54,0.06)")
fill(p2, p3, color="rgba(255,87,34,0.06)")
fill(p3, p4, color="rgba(255,152,0,0.06)")
fill(p4, p5, color="rgba(255,193,7,0.06)")
fill(p5, p6, color="rgba(205,220,57,0.06)")
fill(p6, p7, color="rgba(139,195,74,0.06)")
fill(p7, p8, color="rgba(76,175,80,0.06)")
fill(p8, p9, color="rgba(0,150,136,0.06)")
fill(p9, p10, color="rgba(0,188,212,0.06)")
