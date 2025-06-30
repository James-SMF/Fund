import pandas as pd
from datetime import datetime
from model import compute_rsi

def apply_moving_average_strategy(df: pd.DataFrame, real_time_estimate: float, threshold = 0.015, window=5):
    df = df.copy()
    df['nav'] = df['nav'].astype(float)

    # Append real time estimate at the end of the df as a new nav value
    today_date = datetime.today().strftime('%Y-%m-%d')
    df = df.append({'date': today_date, 'nav': real_time_estimate}, ignore_index=True)

    df['ma'] = df['nav'].rolling(window).mean()
    df['signal'] = 0
    df.loc[df['nav'] > df['ma'], 'signal'] = -1  # 模拟卖出
    df.loc[df['nav'] < df['ma'], 'signal'] = 1  # 模拟买入
    df.loc[df['nav'] > df['ma'] + threshold, 'signal'] = -2
    df.loc[df['nav'] < df['ma'] - threshold, 'signal'] = 2

    return df

def apply_rsi_strategy(df, real_time_estimate, period = 15):
    df = df.copy()
    df['nav'] = df['nav'].astype(float)

    # Append real time estimate at the end of the df as a new nav value
    today_date = datetime.today().strftime('%Y-%m-%d')
    df = df.append({'date': today_date, 'nav': real_time_estimate}, ignore_index=True)

    df['rsi'] = compute_rsi(df['nav'], period)
    df['rsi_signal'] = 0
    df.loc[df['rsi'] >= 70, 'rsi_signal'] = -1
    df.loc[df['rsi'] <= 30, 'rsi_signal'] = 1
    return df
