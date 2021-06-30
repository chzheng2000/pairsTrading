#coding=utf-8
'''
    FileName      ：trade.py
    Author        ：@zch0423
    Date          ：Jun 30, 2021
    Description   ：
    配对交易代码主体部分
'''
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker
import statsmodels.api as sm
import utils  # 一些工具函数


class Arbitrageur:
    '''
    配对交易类，包含配对交易代码和图表绘制
    基于形成期数据用于交易期策略模拟
    '''
    def __init__(self, y, x, model, dates, account=1e6, size=10, 
                open_thsh=1.5, close_thsh=0.5, stop_thsh=3, cost_rate=0):
        '''
        @Description
        初始化
        ------------
        @Params
        y, Series, 高价资产
        x, Series, 低价资产
        model, 协整模型结果
        dates, 交易时间序列
        account, float default 1e6, 初始资金
        size, int default 10, 合约最下交易单位
        open_thsh, float default 1.5, 开仓阈值
        close_thsh, float default 0.5, 平仓阈值
        stop_thsh, float default 3, 止损阈值
        cost_rate, float default 0, 单边交易成本占数额比例
        ------------
        @Returns
        '''
        self.account = account
        self.dates = dates
        temp = len(self.dates)
        self.y = y
        self.x = x
        # 仓位记录
        self.y_pos = 0
        self.x_pos = 0
        # 信号记录
        self.y_signal = [0 for i in range(temp)]
        self.x_signal = [0 for i in range(temp)]
        # 收益记录
        self.profits = [0 for i in range(temp)]  # 收益
        self.returns = [0 for i in range(temp)]  # 收益率

        self.size = size
        self.cost_rate = cost_rate

        # 获取价差和对应范围
        self.setIntervals(model, close_thsh, stop_thsh, open_thsh)

        self.signal = 0  # 交易信号

    def setIntervals(self, model, close_thsh, stop_thsh, open_thsh):
        '''
        @Description
        获取交易期价差
        ------------
        @Returns
        set 
        self.itv, 价差所在区间用于信号
        self.beta, self.alpha 协整参数
        '''
        # 协整模型
        self.alpha = model.params[0]
        self.beta = model.params[1]
        resid = model.resid
        mu = np.mean(resid)
        sd = np.std(resid)
        # 交易期价差
        self.spread = self.y-self.beta*self.x-self.alpha
        # 交易信号区间
        self.level = (float('-inf'), mu-stop_thsh*sd, mu-open_thsh*sd, 
                    mu-close_thsh*sd, mu+close_thsh*sd,
                    mu+open_thsh*sd,mu+stop_thsh*sd, float('inf'))
        # 交易期价差所处范围空间
        self.itv = pd.cut(self.spread, self.level, labels=False)-3

    def getSignal(self, i):
        '''
        @Description
        根据价差位置变化获取信号
        ------------
        @Params
        i, int, 第i天 i>0
        ------------
        @Returns
        '''
        if self.itv[i-1] == 1 and self.itv[i] == 2:
            self.signal = 1  # 反向建仓，超过1.5sd 价差扩大，买x卖y
            self.y_signal[i] = -1
            self.x_signal[i] = 1
        elif self.itv[i-1] == 1 and self.itv[i] == 0:
            self.signal = -1  # 反向平仓，卖x买y
            self.y_signal[i] = 0
            self.x_signal[i] = 0
        elif self.itv[i-1] == -1 and self.itv[i] == -2:
            self.signal = 2  # 正向建仓 买y卖x
            self.y_signal[i] = 1
            self.x_signal[i] = -1
        elif self.itv[i-1] == -1 and self.itv[i] == 0:
            self.signal = -2  # 正向平仓 卖y买x
            self.y_signal[i] = 0
            self.x_signal[i] = 0
        self.signal = 0  # 保持
        self.y_signal[i] = self.y_signal[i-1] 
        self.x_signal[i] = self.x_signal[i-1]
    
    def buildPosition(self, i):
        '''
        @Description
        建仓
        '''
        temp = self.y_signal[i]  # 正负号
        self.y_pos = temp*((self.account/self.y[i])//self.size)*self.size
        buy_y = self.y_pos*self.y[i]
        self.x_pos = (-(buy_y/self.beta/self.x[i])//self.size)*self.size
        buy_x = self.x_pos*self.x[i]
        cost = (abs(buy_y)+abs(buy_x))*self.cost_rate
        self.account_flag = self.account  # 记录
        self.account -= buy_y
        self.account -= buy_x
        self.account -= cost

    def closePosition(self, i):
        '''
        @Description
        平仓 
        '''
        buy_y = -self.y_pos*self.y[i]
        buy_x = -self.x_pos*self.x[i]
        cost = (abs(buy_y)+abs(buy_x))*self.cost_rate
        return_flag = account
        self.account -= buy_y
        self.account -= buy_x
        self.account -= cost
        self.profits[i] = self.account - self.account_flag
        self.returns[i] = self.profits[i]/return_flag
        self.y_pos = 0
        self.x_pos = 0
        self.account_flag = 0 
    
    def trade(self):
        '''
        @Description
        交易期模拟
        ------------
        @Returns
        '''
        for i in range(1, len(self.dates)):
            self.getSignal(i)
            if self.signal==0:
                continue
            # temp = self.y_signal[i]
            elif self.signal > 0:
                self.buildPosition(i)
            elif self.signal < 0:
                self.closePosition(i)

    def getCumProfits(self):
        '''
        @Description
        获取累计收益
        ------------
        @Returns
        cum_profits
        '''
        return np.cumsum(self.profits)

    

def main():
    data, pairs, models = utils.loadData()
    # account=1e6
    # size=10
    # open_thsh=1.5
    # close_thsh=0.5
    # stop_thsh=3
    # cost_rate=0
    # 交易期设置
    start, end = utils.getDateIdx(data, "2019-01-01", "2020-01-01")
    slices = [slice(0, 5), slice(0, 10), 
        slice(0, 20), slice(0, None), 
        slice(-5,None), slice(-10, None),
        slice(-20, None)]
    dates = np.sort(data["date"].unique())[start:end]
    for s in slices:
        for cost in np.arange(0, 0.011, 0.001):
            for open_thsh in [1, 1.5, 2, 2.5]:
                for i, model in models[s]:
                    asset1, asset2 = pairs[i][0].split("-")
                    # 获取交易期数据
                    y = utils.getPrice(data, asset1, start, end)
                    x = utils.getPrice(data, asset2, start, end)
                    tradebot = Arbitrageur(y, x, model, dates,  
                    open_thsh=open_thsh, cost_rate=cost)
                    tradebot.trade()
                    profits = tradebot.getCumProfits()
                    # print(profits)
                    # anything to explore further
                    #####################

if __name__ == "__main__":
    main()


    