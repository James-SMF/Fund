import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from matplotlib import font_manager
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)  # 避免除0
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_ma(series, window):
    return series.rolling(window=window).mean()

def compute_volatility(series, window=5):
    return series.rolling(window=window).std()

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2  # macd柱
    return dif, dea, macd

def time_series_prediction(csv_file, window_size, n, max_depth, lr, param_mode = False):
    # ==== 1. 读取并准备数据 ====
    df = pd.read_csv(csv_file)  # 替换为你的 CSV 文件名
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # 创建标签列：预测是否上涨
    df['target'] = (df['nav'].shift(-1) > df['nav']).astype(int)

    df['rsi14'] = compute_rsi(df['nav'], period=14)
    df['ma5'] = compute_ma(df['nav'], window=5)
    df['volatility'] = compute_volatility(df['nav'], window=5)
    #  df['macd_dif'], df['macd_dea'], df['macd_bar'] = compute_macd(df['nav'])
    df = df.dropna().reset_index(drop=True)

    # 设置历史窗口长度
    features = []
    targets = []
    dates = []

    for i in range(window_size, len(df)-1):  # -1是因为最后一行不能预测
        value_window = df['nav'].iloc[i-window_size:i].values
        label = df['target'].iloc[i]
        date = df['date'].iloc[i]
        rsi_val = df['rsi14'].iloc[i]
        ma_val = df['ma5'].iloc[i]
        volatility = df['volatility'].iloc[i]

        feature = np.concatenate([value_window, [rsi_val, ma_val, volatility]])
        features.append(feature)
        targets.append(label)
        dates.append(date)

    X = np.array(features)
    y = np.array(targets)
    dates = np.array(dates)

    # ==== 2. 切分并训练模型 ====

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.15)

    #  model = RandomForestClassifier(n_estimators=n, random_state=42)
    model = XGBClassifier(
        n_estimators=n,
        max_depth=max_depth,
        learning_rate=lr,
        use_label_encoder=False,
        eval_metric='logloss',  # 避免警告
        random_state=42
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("Accuracy:", acc)

    return df, y_test, y_pred, acc

def plot_ml_prediction(df, y_test, y_pred, window_size):
    # 确保索引对齐
    test_index = df.iloc[window_size:len(df)-1].index[-len(y_test):]
    df_test = df.loc[test_index].copy()
    df_test['pred'] = y_pred

    # 1. 绘制预测 vs 实际
    plt.figure(figsize=(14, 6))
    plt.plot(df_test['date'], df_test['target'], label='实际涨跌（1=涨，0=跌）', color='blue', marker='o')
    plt.plot(df_test['date'], df_test['pred'], label='预测涨跌', color='orange', marker='x', linestyle='--')

    # 2. 标出预测正确和错误的点
    correct = df_test[df_test['target'] == df_test['pred']]
    wrong = df_test[df_test['target'] != df_test['pred']]

    plt.scatter(correct['date'], correct['target'], color='green', label='预测正确', marker='o')
    plt.scatter(wrong['date'], wrong['target'], color='red', label='预测错误', marker='x')

    # 3. 设置标题和图例
    plt.title("模型预测 vs 实际涨跌趋势")
    plt.xlabel("日期")
    plt.ylabel("涨跌（1=涨，0=跌）")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    data_file = 'data/012553.csv'

    param_mode = False

    if param_mode:
        cur_max = 0
        cur_max_window = 0
        cur_max_n = 0
        cur_max_d = 0
        cur_max_lr = 0

        for n in tqdm(range(100, 150, 5)):
            for window_size in range(3, 10):
                for max_depth in range(3, 7):
                    for lr_100 in range(1, 30, 2):
                        lr = lr_100 / 100
                        df, y_test, y_pred, acc = time_series_prediction(
                            data_file,
                            window_size,
                            n,
                            max_depth,
                            lr,
                            param_mode
                        )

                    if acc > 0.7 and acc >= cur_max:
                        cur_max = acc
                        cur_max_window = window_size
                        cur_max_n = n
                        cur_max_d = max_depth
                        cur_max_lr = lr
                        print('==================================')
                        print('新的最优参数！')
                        print('准确率:', acc)
                        print('window_size:', window_size)
                        print('n_estimators:', n)
                        print('max_depth:', max_depth)
                        print('lr:', lr)
                        print('==================================\n')
    else:
        window_size = 6
        n = 185
        max_depth = 2
        lr = 0.29
        df, y_test, y_pred, acc = time_series_prediction('data/012553.csv', window_size, n, max_depth, lr)
        plot_ml_prediction(df, y_test, y_pred, window_size)
