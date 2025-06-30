import pandas as pd
import matplotlib.pyplot as plt
from model import compute_rsi

def data_cleaning(fund_code):
    csv_file = f'data/{fund_code}.csv'
    df = pd.read_csv(csv_file)  # 替换为你的 CSV 文件名
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    nav_list = list(zip(df['date'], df['nav']))
    return nav_list

def simulator(nav_list):
    # 假设起始资金2000元
    initial_money = fund_amount = 20000
    total_money = 0
    last_operating_nav = 1

    ma_window = []
    rsi_window = []
    strategy_list = []
    avg_nav = 0

    for date, nav in nav_list:
        # 1 买入
        # -1 卖出
        # 0 保持
        ma_flag = 0
        rsi_flag = 0
        absolute_flag = 0
        avg_flg = 0
        ma_amount = 0
        absolute_amount = 0

        # ===================================

        if len(ma_window) < 5:
            ma_window.append(nav)
        else:
            ma_window.pop(0)
            ma_window.append(nav)
            ma = sum(ma_window) / len(ma_window)

            if nav > ma + 0.001:
                ma_flag = -1
            elif nav < ma - 0.03:
                ma_flag = 1

            #  if ma_flag != 0:
                #  ma_amount = abs(nav - ma) * 0

        # ===================================

        if len(rsi_window) < 14:
            rsi_window.append(nav)
        else:
            rsi_window.pop(0)
            rsi_window.append(nav)
            rsi_series = pd.Series(rsi_window)
            rsi = compute_rsi(rsi_series, 14)

            rsi = rsi.iloc[-1]

            if rsi > 50:
                rsi_flag = 1
            elif rsi < 50:
                rsi_flag = -1

        # ===================================

        if len(strategy_list) == 0:
            change_ratio = (nav - last_operating_nav) / last_operating_nav
        else:
            if strategy_list[-1][0] == 0:
                if nav > last_operating_nav:
                    for strategy_index in range(len(strategy_list) - 1, -1, -1):
                        if strategy_list[strategy_index][0] == 1:
                            change_ratio = (nav - strategy_list[strategy_index][2]) / strategy_list[strategy_index][2]
                            break
                    if strategy_index <= 0:
                        change_ratio = (nav - last_operating_nav) / last_operating_nav
                else:
                    change_ratio = (nav - last_operating_nav) / last_operating_nav

            elif strategy_list[-1][0] == 1:
                if nav < last_operating_nav:
                    for strategy_index in range(len(strategy_list) - 1, -1, -1):
                        if strategy_list[strategy_index][0] == 0:
                            change_ratio = (nav - strategy_list[strategy_index][2]) / strategy_list[strategy_index][2]
                            break

                    if strategy_index <= 0:
                        change_ratio = (nav - last_operating_nav) / last_operating_nav
                else:
                    change_ratio = (nav - last_operating_nav) / last_operating_nav


        if change_ratio > 0.013:
            absolute_flag = -1
        elif change_ratio < -0.013:
            absolute_flag = 1

        #  if absolute_flag != 0:
            #  absolute_amount = abs(change_ratio) * 1500

        if absolute_flag == 1:
            absolute_amount = abs(change_ratio) * 1880
        elif absolute_flag == -1:
            absolute_amount = abs(change_ratio) * 1443



        # ===================================

        if len(strategy_list) == 0:
            avg_nav = nav
        else:
            avg_nav = (avg_nav * (len(strategy_list) - 1) + nav) / len(strategy_list)

        avg_percentage = nav - avg_nav
        avg_flag = -1 if avg_percentage > 0 else 1

        # ===================================

        #  if absolute_flag == ma_flag and ma_flag != 0 and rsi_flag == ma_flag:
        if absolute_flag == ma_flag and ma_flag != 0:
            money = absolute_amount

            # 当前净值比均值高，那么卖的多，买的少。反之。
            if avg_flag == -1:
                money *= 1 - ma_flag * avg_percentage
            else:
                money *= 1 + ma_flag * avg_percentage

            fund_amount += money * ma_flag
            total_money -= money * ma_flag

            if ma_flag < 0:
                print(f'Sell {date} {nav} {fund_amount} --- {money}')
            else:
                print(f'Buy {date} {nav} {fund_amount} --- {money}')


            last_operating_nav = nav
            strategy_list.append([int(ma_flag > 0), date, nav])


    print('最终基金份额:', fund_amount)
    print('换算基金金额:', fund_amount * nav)
    print('手里剩余资金的变化:', total_money)
    print('总资金:', total_money + fund_amount * nav)
    print('累计盈亏:', total_money + fund_amount * nav - initial_money)
    print('基准盈亏:', (nav-1) * initial_money)


    df_nav = pd.DataFrame(nav_list, columns=["date", "nav"])
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    df_nav.set_index("date", inplace=True)

    df_trade = pd.DataFrame(strategy_list, columns=["signal", "date", "value"])
    df_trade["date"] = pd.to_datetime(df_trade["date"])

    plt.figure(figsize=(12, 6))
    plt.plot(df_nav.index, df_nav["nav"], label="Net Asset Value", color="blue")

    # 筛选买入/卖出信号
    buy_signals = df_trade[df_trade["signal"] == 1]
    sell_signals = df_trade[df_trade["signal"] == 0]

    # 画买入点
    plt.scatter(buy_signals["date"], buy_signals["value"], color="green", label="Buy", marker="^", s=100)

    # 画卖出点
    plt.scatter(sell_signals["date"], sell_signals["value"], color="red", label="Sell", marker="v", s=100)

    plt.title("Fund NAV with Buy/Sell Signals")
    plt.xlabel("Date")
    plt.ylabel("Net Asset Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()



if __name__ == '__main__':
    fund_code = '012553'
    nav_list = data_cleaning(fund_code)
    simulator(nav_list)
