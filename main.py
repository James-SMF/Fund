from fetcher import fetch_fund_nav, fetch_fund_estimate
from strategy import apply_moving_average_strategy
from plotter import plot_strategy

def main():
    fund_code = '021580'
    print("正在抓取基金数据...")
    df = fetch_fund_nav(fund_code, 90)

    print("\n=== 获取当前净值估算（适合下午2:50运行） ===")
    estimate = fetch_fund_estimate(fund_code)
    print("当前估算净值:", estimate)

    print("数据抓取完成，正在应用策略...")
    df = apply_moving_average_strategy(df, estimate['估算净值'], threshold=0.015, window=5)

    print("策略计算完成，正在绘图...")
    plot_strategy(df)

if __name__ == '__main__':
    main()

