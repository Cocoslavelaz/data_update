import pandas as pd 
from conn_postgre import conn_postgre
from datetime import date
from datetime import  timedelta
from get_stock import get_close
from conn_postgre import insert_data

# 初始化日期
today = date.today()
tomorrow = today + timedelta(days=1)
tomorrow_str = tomorrow.strftime('%Y-%m-%d')

# 读取股票代码
code_list = pd.read_csv("all_etf.csv", header=None)
code_list = code_list[1].iloc[1:271]

def update_etf_close(start='2024-12-11', end='2024-12-21'):
    code_list_tw = [code.replace("_close", "") + ".Tw" for code in code_list]
    df = pd.DataFrame()
    for index, code in enumerate(code_list_tw):
        stock_data = get_close(code, start=start, end=end).reset_index()
        stock_data.fillna(0, inplace=True)  # 填充缺失值
        stock_data = stock_data.rename(columns={"Date": "date", "Adj Close": code_list.iloc[index] + "_close"})
        
        if df.empty:
            df = stock_data[["date", code_list.iloc[index] + "_close"]]
        else:
            df = pd.merge(df, stock_data[["date", code_list.iloc[index] + "_close"]], on="date", how="outer")

    df = df.sort_values(by="date").reset_index(drop=True)
    df.columns = [col.rstrip('_close') if col.endswith('_close') else col for col in df.columns]
    df.columns = [col + '_close' if col != 'date' else col for col in df.columns]
    insert_data("all_etf_close",df)
    return "update completed"

if __name__ == "__main__":
    print(update_etf_close())
