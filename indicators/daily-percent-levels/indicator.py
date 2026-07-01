from tg_scripting import *
import numpy as np

indicator("Daily Percent Levels", overlay=True)

num_levels = input.int(6, "Number of Levels", minval=2, maxval=10)
step_pct = input.float(0.5, "Step Percent", minval=0.1, maxval=2.0, step=0.1)

cl = np.array(close, dtype=float)
n = len(cl)

if n < 2:
    pass
else:
    ref_price = float(cl[0])

    green_colors = ["#4CAF50", "#66bb6a", "#81c784", "#a5d6a7", "#c8e6c9",
                    "#43a047", "#2e7d32", "#1b5e20", "#388e3c", "#00c853"]
    red_colors = ["#f44336", "#ef5350", "#e57373", "#ef9a9a", "#ffcdd2",
                  "#e53935", "#c62828", "#b71c1c", "#d32f2f", "#ff1744"]

    for i in range(num_levels):
        pct = step_pct * (i + 1)
        above = ref_price * (1 + pct / 100)
        below = ref_price * (1 - pct / 100)

        g_color = green_colors[i % len(green_colors)]
        r_color = red_colors[i % len(red_colors)]

        line.new(x1=0, y1=above, x2=n - 1, y2=above,
                 color=g_color, width=1, style=line.style_dashed)
        label.new(x=n - 1, y=above,
                  text=f"+{pct:.1f}% ({above:.2f})",
                  style=label.style_label_left, color="rgba(0,0,0,0)",
                  textcolor=g_color, size="tiny")

        line.new(x1=0, y1=below, x2=n - 1, y2=below,
                 color=r_color, width=1, style=line.style_dashed)
        label.new(x=n - 1, y=below,
                  text=f"-{pct:.1f}% ({below:.2f})",
                  style=label.style_label_left, color="rgba(0,0,0,0)",
                  textcolor=r_color, size="tiny")

    line.new(x1=0, y1=ref_price, x2=n - 1, y2=ref_price,
             color="#888888", width=2, style=line.style_solid)
    label.new(x=n - 1, y=ref_price,
              text=f"Ref ({ref_price:.2f})",
              style=label.style_label_left, color="rgba(0,0,0,0)",
              textcolor="#888888", size="tiny")
