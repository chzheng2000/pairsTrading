#coding=utf-8
'''
    FileName      ：dataPreprocess.py
    Author        ：@zch0423
    Date          ：Jun 30, 2021
    Description   ：
    CSMAR数据预处理，导出csv和bin文件
'''
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

def majorContract(group):
    '''
    @Description
    生成最大成交量列，用于groupby聚合函数
    ------------
    @Params
    group, pd.groupby
    ------------
    @Returns
    group
    '''
    maxVol = group["Fdt010"].max()
    group["max"] = maxVol
    return group

def findLiquid(data, min_vol=100):
    '''
    @Description
    寻找流动性好的合约
    ------------
    @Params
    data, pd.DataFrame
    min_vol, int default 100, 最低成交量
    ------------
    @Returns
    data, 四列["date", "asset", "close", "volume"]
    '''
    # 根据成交量筛选出主力合约
    data = data.groupby(["Trddt", "Trdvar"]).apply(majorContract)
    data = data[data["Fdt010"]==data["max"]]
    # 去除主力合约成交量过小的期货，如中密度纤维板、早籼稻等
    data = data[data["max"]>min_vol]
    data = data[["Trddt", "Trdvar", "Fdt006", "Fdt010"]]
    # 去除某一日无交易的品种
    tradvars = data["Trdvar"].unique()
    num_days = data.groupby("Trdvar")["Trddt"].count()
    # 没有交易空缺
    total_days = (num_days == num_days.max()) 
    data = data[data["Trdvar"].map(total_days)]
    # 重命名列
    data.columns = ["date", "asset", "close", "volume"]
    return data

def getCumReturn(data):
    '''
    @Description
    获取累计收益率
    ------------
    @Params
    data, DataFrame, ["date", "asset", "close", "volume"]
    ------------
    @Returns
    cum_returns, dict, {asset:return}
    '''
    # 转化成时间格式
    data.loc[:,"date"] = pd.to_datetime(data["date"], format="%Y-%m-%d")
    cum_returns = {}
    for asset in data["asset"].unique():
        temp = data[data["asset"] ==asset].sort_values(by="date")["close"]
        # 收益率
        temp = (temp - temp.shift(1))/temp.shift(1) 
        # 累计收益率
        temp = (1+temp).cumprod()
        cum_returns[asset] = temp
    return cum_returns

def main():
    data = pd.read_csv("data/FUT_Fdt.csv")
    # 流动性合约
    data = findLiquid(data, min_vol=100)
    # 导出
    data.to_csv("data/preprocessed.csv", index=False)
    # 计算累计收益率
    cum_returns = getCumReturn(data)
    # 导出
    with open("data/cumReturn.bin", "wb") as f:
        pickle.dump(cum_returns, f)
        f.close()

if __name__ == "__main__":
    main()




