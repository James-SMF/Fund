import pandas as pd
from datetime import datetime
from data.last_10_transactions import last_10_transactions

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

    diff = df['nav'] - df['ma']
    print(diff.iloc[-1])
    print(df['ma'])

    today_amount = diff.iloc[-1] / 0.0005
    print(f'当前估算净值：{real_time_estimate}，策略执行结果：{df["signal"].iloc[-1]}，今日建议操作金额比例：{today_amount}%')
    return df

#  def last_transaction_based_strategy(df):
    #  if len(last_10_transactions['005644']) < 1:
