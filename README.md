## 基于协整的期货配对交易模型
- 数据来源CSMAR

dataProcess
- 预处理数据

findPairs
- 根据最小距离找到价格对，导出到SSDs.bin

cointegration
- 根据形成期构建协整模型，进行协整检验等

trading
- 交易模块，根据协整模型进行交易
