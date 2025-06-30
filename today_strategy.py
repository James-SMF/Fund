from data.last_transaction import last_transaction

def daily_strategy_based_on_ma(df):
    diff = df['nav'] - df['ma']
    today_amount = diff.iloc[-1] / 0.0005

    return df["signal"].iloc[-1], today_amount

def daily_strategy_based_on_last_transaction(fund_id, real_time_estimate):
    last_trans, total_money = last_transaction[fund_id]
    if last_trans is None:
        # 买入200，建仓
        return 2, 200

    diff = real_time_estimate - last_trans

    diff_ratio = diff / last_trans
    sell_buy_flag = 0
    if diff_ratio > 0.02:
        sell_buy_flag = 2
    elif diff_ratio < -0.02:
        sell_buy_flag = -2

    today_amount = 0 if sell_buy_flag == 0 else 200
    return sell_buy_flag, today_amount

def daily_strategy_based_on_rsi(df):
    amount = 200
    if df["rsi"].iloc[-1] >= 70 :
        amount += 20 * (df["rsi"].iloc[-1] - 70)
    elif df["rsi"].iloc[-1] <= 30 :
        amount -= 20 * (30 - df["rsi"].iloc[-1])

    return df["rsi_signal"].iloc[-1], amount
