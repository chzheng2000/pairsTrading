#coding=utf-8
'''
    FileName      ：findPairs.py
    Author        ：@zch0423
    Date          ：Jun 30, 2021
    Description   ：
    根据最小距离和协整筛选配对
'''
import pickle
from itertools import combinations
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from utils import getPrice, getDateIdx, getDPrice, normalize

def calSSD(x1, x2):
    return np.sum((x1-x2)**2)

def calSSDs(data, cum_returns, start, end):
    '''
    @Description
    计算所有配对组合的最小距离SSD
    ------------
    @Params
    data, DataFrame
    cum_returns, dict, 累计收益率
    start, int, 形成期开始下标
    end, int, 形成期结束下标
    ------------
    @Returns
    SSDs, dict, {"asset1-asset2", SSD}其中asset1为高价资产
    '''
    # 两两组合计算SSDs
    SSDs = {}
    for asset1, asset2 in combinations(cum_returns.keys(), 2):
        x1 = cum_returns[asset1].dropna().values[start:end]
        x2 = cum_returns[asset2].dropna().values[start:end]
        return1 = normalize(x1)
        return2 = normalize(x2)

        # 保证asset1为高价资产
        p1 = getPrice(data, asset1, start, end)
        p2 = getPrice(data, asset2, start, end)
        if np.mean(p1)<np.mean(p2):
            asset1, asset2 = asset2, asset1

        SSDs[f"{asset1}-{asset2}"] = calSSD(return1, return2)  

    # 按SSD大小排序
    SSDs = sorted(SSDs.items(), key=lambda d:d[1])
    return SSDs 

def cointegration(data, SSDs, start, end, alpha=0.5):
    '''
    @Description
    根据协整寻找配对
    ------------
    @Params
    data, DataFrame
    SSDs, dict, SSD配对
    start, end, int 时间下标
    alpha, float default 0.5 置信度水平
    ------------
    @Returns
    models, list, [index, result]
    '''
    models = []  # 保存序号和回归结果
    for idx, value in enumerate(SSDs):
        pair1, pair2 = value[0].split("-")
        y = getPrice(data, pair1, start, end)
        x = getPrice(data, pair2, start, end)
        # 单位根检验 pvalue
        if adfuller(y)[1]<alpha or adfuller(x)[1]<alpha:
            continue
        # 一阶差分单位根检验 pvalue
        p1 = adfuller(getDPrice(data, pair1, start, end))[1]
        p2 = adfuller(getDPrice(data, pair2, start, end))[1]
        if p1>alpha or p2>alpha:
            continue
        # 检验协整关系 
        X = sm.add_constant(x)
        result = sm.OLS(y, X).fit()
        # print(result.summary()) # 回归结果

        # 残差单位根检验
        if adfuller(result.resid)[1] > alpha:
            continue
        models.append([idx, result])
    return models

def main():
    data = pd.read_csv("data/preprocessed.csv")
    with open("data/cumReturn.bin", "rb") as f:
        cum_returns = pickle.load(f)
        f.close()

    # 形成期
    start_date="2018-01-01"
    end_date="2019-01-01"
    start, end = getDateIdx(data, start_date, end_date)
    # SSDs = calSSDs(data, cum_returns, start, end)

    # 导出SSDs
    # with open("data/SSDs.bin", "wb") as f:
    #     pickle.dump(SSDs, f)
    #     f.close()

    # 导入SSDs
    with open("data/SSDs.bin", "rb") as f:
        SSDs = pickle.load(f)
        f.close()

    # models = cointegration(data, SSDs, start, end, alpha=0.05)

    # 导出models
    # with open("data/models.bin", "wb")as f:
    #     pickle.dump(models, f)
    #     f.close()

    # 导入models
    with open("data/models.bin", "rb") as f:
        models = pickle.load(f)
        f.close()

    # 导出具有协整关系的商品配对
    idxs = list(map(lambda x:x[0], models))
    pairs = [SSDs[i] for i in idxs]
    
    # 导出pairs
    # with open("data/pairs.bin", "wb") as f:
    #     pickle.dump(pairs, f)
    #     f.close()

if __name__ == "__main__":
    main()
    