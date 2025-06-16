import pandas as pd
import matplotlib.pyplot as plt

def plot_strategy(df: pd.DataFrame):
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['nav'], label='NAV', color='blue')
    plt.plot(df['date'], df['ma'], label='MA(5)', color='orange')

    # 画出信号点
    #  buy = df[df['signal'] == 1]
    #  sell = df[df['signal'] == -1]
    buy = df[df['signal'] == 2]
    sell = df[df['signal'] == -2]

    plt.scatter(buy['date'], buy['nav'], label='Buy', marker='^', color='green')
    plt.scatter(sell['date'], sell['nav'], label='Sell', marker='v', color='red')

    plt.xticks(rotation=45)
    plt.legend()
    plt.title('基金净值与均线策略')
    plt.tight_layout()
    plt.show()

