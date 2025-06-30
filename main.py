from fetcher import fetch_fund_nav, fetch_fund_estimate
from strategy import *
from plotter import plot_strategy
import today_strategy

def main(plot = True):
    fund_code = '021580'
    print("正在抓取基金数据...")
    df = fetch_fund_nav(fund_code, 90)

    print("\n=== 获取当前净值估算（适合下午2:50运行） ===")
    estimate = fetch_fund_estimate(fund_code)
    print("当前估算净值:", estimate)

    print("数据抓取完成，正在应用策略...")
    df = apply_moving_average_strategy(df, estimate['估算净值'], threshold=0.015, window=5)
    df = apply_rsi_strategy(df, estimate['估算净值'], period=15)

    if plot:
        print("策略计算完成，正在绘图...")
        plot_strategy(df)

    # ===========================================
    # 开始执行策略
    # ===========================================

    print("\n\n\n五日均线建议：")
    signal, today_amount = today_strategy.daily_strategy_based_on_ma(df)

    strategy_map = {
        1: '看空，但不建议此时加仓',
        2: '建议加仓',
        -1: '看多，但不建议此时抛掉',
        -2: '建议抛掉',
        0: '忍住，别做任何操作'
    }

    print(f'策略执行结果：{strategy_map[signal]}，今日建议操作金额比例：{today_amount}%')

    print("\n\n历史买卖记录建议：")
    signal, today_amount = today_strategy.daily_strategy_based_on_last_transaction(fund_code, estimate['估算净值'])
    print(f'策略执行结果：{strategy_map[signal]}，今日建议操作金额：{today_amount}元')

if __name__ == '__main__':
    main(False)

