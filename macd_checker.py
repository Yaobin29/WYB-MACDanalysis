# macd_checker.py

import yfinance as yf
import pandas as pd
from notion_utils import write_macd_to_notion
import json
from datetime import datetime, timezone

def calculate_macd(df, fast=12, slow=26, signal=9):
    df["EMA_fast"] = df["Close"].ewm(span=fast, adjust=False).mean()
    df["EMA_slow"] = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = df["EMA_fast"] - df["EMA_slow"]
    df["Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    df["Histogram"] = df["MACD"] - df["Signal"]
    return df

def classify_macd(df):
    macd_line = df["MACD"]
    signal_line = df["Signal"]
    hist = df["Histogram"]
    price = df["Close"]

    if len(df) < 3:
        return None

    if macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
        # 金叉
        if macd_line.iloc[-1] > 0:
            return ("金叉", "0轴上", "强金叉", "MACD上穿信号线且在0轴之上，趋势强")
        elif min(hist.iloc[-5:]) < -3 and hist.iloc[-1] > hist.iloc[-2] and price.iloc[-1] > min(price.iloc[-10:]):
            return ("金叉", "0轴下", "底部反转金叉", "MACD下方金叉+极端柱状图缩小+价格回升")
        else:
            return ("金叉", "0轴下", "弱金叉", "MACD下方金叉但动能未明显增强")
        
    elif macd_line.iloc[-2] > signal_line.iloc[-2] and macd_line.iloc[-1] < signal_line.iloc[-1]:
        # 死叉
        if macd_line.iloc[-1] > 0:
            return ("死叉", "0轴上", "强死叉", "MACD死叉在0轴上方，警惕回调")
        else:
            return ("死叉", "0轴下", "弱死叉", "MACD死叉在0轴下方，空头趋势延续")
        
    return ("无", "-", "-", "无明显MACD交叉")

def main():
    # 加载股票列表
    with open("stock_list.json", "r") as f:
        tickers = json.load(f)

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="3mo", interval="1d", progress=False)
            if data.empty:
                print(f"❌ 无法获取数据：{ticker}")
                continue

            df = calculate_macd(data)
            result = classify_macd(df)

            # 获取最近交易日日期（UTC 转 ISO）
            last_date = df.index[-1].to_pydatetime().replace(tzinfo=timezone.utc).isoformat()

            write_macd_to_notion(ticker, last_date, *result)
            print(f"✅ {ticker} 写入完成：{result}")

        except Exception as e:
            print(f"⚠️ {ticker} 报错：{e}")

if __name__ == "__main__":
    main()
