from tg_scripting import *

length = input.int(20, "Length", minval=5, maxval=200)
high_corr = input.float(0.7, "High Correlation", minval=0.3, maxval=1.0)
low_corr = input.float(-0.7, "Low Correlation", minval=-1.0, maxval=-0.3)

corr = ta.correlation(close, volume, length)
corr_sma = ta.sma(corr, 5)

plot(corr, title="Correlation", color="#42A5F5")
plot(corr_sma, title="Signal", color="#FF7043")
h_hi = hline(high_corr, title="High Correlation", color="rgba(102,187,106,0.5)")
h_lo = hline(low_corr, title="Low Correlation", color="rgba(239,83,80,0.5)")
hline(0, title="Zero", color="rgba(128,128,128,0.3)")

bgcolor(corr > high_corr, color="rgba(102,187,106,0.06)")
bgcolor(corr < low_corr, color="rgba(239,83,80,0.06)")
