#coding=utf-8
'''
    FileName      ：utils.py
    Author        ：@zch0423
    Date          ：Jun 30, 2021
    Description   ：
    一些工具函数
'''
import numpy as np
import pandas as pd
import pickle 

def getPrice(data, asset, start, end):
    '''
    @Description
    获取名称为asset的前t价格序列
    ------------
    @Params
    data, DataFrame
    asset, str, 资产名称
    start, end, int 时间下标
    ------------
    @Returns
    prices, array
    '''
    return data[data["asset"]==asset].sort_values(by=["date"]).iloc[start:end, 2].values

def getDPrice(data, asset, start, end):
    '''
    @Description
    获取一阶差分序列
    ------------
    @Params
    data, DataFrame
    asset, str, 资产名称
    start, end, int 时间下标
    ------------
    @Returns
    prices, array
    '''
    temp = data[data["asset"]==asset].sort_values(by=["date"]).iloc[start:end, 2]
    return (temp - temp.shift(1)).dropna().values

def getDateIdx(data, start_date="2018-01-01", end_date="2019-01-01"):
    '''
    @Description
    获取日期对应下标
    ------------
    @Params
    data, DataFrame
    start_date, str default 2018-01-01, 形成期开始 
    end_date, str, 形成期结束日期
    ------------
    @Returns
    start, end, int, 日期对应序号
    '''
    # 指定形成期
    dates = data["date"].unique()
    start = sum(dates<=start_date)
    end = sum(dates<=end_date)
    return start, end

def normalize(x):
    '''
    @Description
    min-max归一
    ------------
    @Params
    x, Series
    ------------
    @Returns
    x1, Series
    '''
    return (x-x.min())/(x.max()-x.min())

def loadData():
    '''
    @Description
    导入相关数据
    ------------
    @Returns
    data, pd.Dataframe, 数据
    pairs, list, ('白糖-锌', 2.09) 包含配对和距离
    models, list, (序号, result)
    '''
    # 数据
    data = pd.read_csv("data/preprocessed.csv")
    # 具有协整关系的商品合约配对
    with open("data/pairs.bin", "rb") as f:
        pairs = pickle.load(f)
        f.close()
    # 配对形成期协整模型
    with open("data/models.bin", "rb")as f:
        models = pickle.load(f)
        f.close()
    return data, pairs, models  
    