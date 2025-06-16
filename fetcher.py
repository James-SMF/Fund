import requests
import re
import json
import pandas as pd
from datetime import datetime

def fetch_fund_nav(fund_code: str) -> pd.DataFrame:
    url = f"http://fund.eastmoney.com/pingzhongdata/{fund_code}.js"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    resp = requests.get(url, headers=headers)
    data = resp.text

    pattern = r'Data_netWorthTrend\s*=\s*(\[\{.*?\}\])'
    match = re.search(pattern, data)
    if not match:
        raise Exception("没有这支屌毛基金")

    records = json.loads(match.group(1))
    df = pd.DataFrame([{
        'date': datetime.fromtimestamp(item['x'] / 1000).strftime('%Y-%m-%d'),
        'nav': item['y']
    } for item in records])

    df = df.tail(90)

    df.to_csv(f"data/{fund_code}.csv", index=False)
    return df

def fetch_fund_estimate(fund_code: str) -> dict:
    url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
    headers = { "User-Agent": "Mozilla/5.0" }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None

    try:
        json_str = resp.text.strip()[resp.text.index('{'):-2]
        data = json.loads(json_str)
        return {
            '基金名称': data['name'],
            '估算净值': float(data['gsz']),
            '估算涨幅': data['gszzl'] + '%',
            '估算时间': data['gztime']
        }
    except Exception as e:
        print("估算数据解析失败：", e)
        return None
