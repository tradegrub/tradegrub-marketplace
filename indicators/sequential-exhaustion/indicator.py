from tg_scripting import *
import numpy as np

n = len(close)
setup_count = np.zeros(n)
countdown_count = np.zeros(n)
setup_dir = np.zeros(n)  # 1=bullish, -1=bearish
in_countdown = np.zeros(n)
countdown_dir = np.zeros(n)
completed_9 = np.full(n, np.nan)
completed_13 = np.full(n, np.nan)

for i in range(4, n):
    c = float(close[i])
    c4 = float(close[i - 4])

    # Setup phase
    if c > c4:
        if float(setup_dir[i - 1]) >= 0:
            setup_count[i] = float(setup_count[i - 1]) + 1
            setup_dir[i] = 1
        else:
            setup_count[i] = 1
            setup_dir[i] = 1
    elif c < c4:
        if float(setup_dir[i - 1]) <= 0:
            setup_count[i] = float(setup_count[i - 1]) - 1
            setup_dir[i] = -1
        else:
            setup_count[i] = -1
            setup_dir[i] = -1
    else:
        setup_count[i] = 0
        setup_dir[i] = 0

    # Check for completed 9
    if float(setup_count[i]) == 9:
        completed_9[i] = 9
        in_countdown[i] = 1
        countdown_dir[i] = 1  # sell countdown after bullish setup
        countdown_count[i] = 0
    elif float(setup_count[i]) == -9:
        completed_9[i] = -9
        in_countdown[i] = 1
        countdown_dir[i] = -1  # buy countdown after bearish setup
        countdown_count[i] = 0
    elif bool(in_countdown[i - 1]):
        in_countdown[i] = 1
        countdown_dir[i] = float(countdown_dir[i - 1])
        prev_cd = float(countdown_count[i - 1])

        if float(countdown_dir[i]) == 1:
            # Sell countdown: close > high[2]
            if i >= 2 and c > float(high[i - 2]):
                countdown_count[i] = prev_cd + 1
            else:
                countdown_count[i] = prev_cd
        else:
            # Buy countdown: close < low[2]
            if i >= 2 and c < float(low[i - 2]):
                countdown_count[i] = prev_cd + 1
            else:
                countdown_count[i] = prev_cd

        if float(countdown_count[i]) == 13:
            completed_13[i] = 13 if float(countdown_dir[i]) == 1 else -13
            in_countdown[i] = 0
            countdown_count[i] = 0

plot(setup_count, title="Setup Count", color="#2196F3")
plot(countdown_count, title="Countdown", color="#FF9800")
hline(9, title="Setup Complete", color="rgba(76,175,80,0.5)")
hline(-9, title="Bearish Setup", color="rgba(244,67,54,0.5)")
hline(0, title="Zero", color="rgba(128,128,128,0.3)")

plotshape(~np.isnan(completed_9) & (completed_9 > 0), title="Bullish 9", style="triangleup", location="bottom", color="#4CAF50")
plotshape(~np.isnan(completed_9) & (completed_9 < 0), title="Bearish 9", style="triangledown", location="top", color="#F44336")
plotshape(~np.isnan(completed_13) & (completed_13 > 0), title="Sell 13", style="diamond", location="top", color="#FF5722")
plotshape(~np.isnan(completed_13) & (completed_13 < 0), title="Buy 13", style="diamond", location="bottom", color="#009688")
