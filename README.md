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

## 中间数据
- preprocessed.csv 满足要求的35个品种
- cumReturn.bin 累计收益率
- SSDs.bin 按SSD排序的{}-{}配对
- paris.bin 通过协整检验的剩余配对
- models.bin [(SSDs id, model, result)]



## 整理

画图代码在notebook中

新代码整理成py文件

