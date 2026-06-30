import pandas as pd
import pandas_ta as ta

def run(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    rsi_period = params.get("rsi_period", 14)
    df["rsi"] = ta.rsi(df["close"], length=rsi_period)
    df["signal"] = 0
    df.loc[df["rsi"] < 30, "signal"] = 1
    df.loc[df["rsi"] > 50, "signal"] = -1
    return df
