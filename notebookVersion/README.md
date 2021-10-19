## 配对交易
### 文件说明
- TRD_Dalyr.xlsx，原始文件，数据来源CSMAR，选取了A股主板非ST股票
- data.bin，中间结果，股票代码和df对应的字典
- SSD.bin，最小距离配对结果
- models.bin，协整模型保存
- tradeLog.txt, top100配对交易明细
### 实现思路
- 数据预处理，导出每只股票对应的价格序列到data.bin
- 根据最小距离从小到大对股票配对进行排序，结果保存到SSD.bin
- 对价格序列进行一阶单整检验，通过的序列进一步构建协整模型，对残差进行单位根检验，保留符合要求的配对
- 根据形成期设定开平仓阈值，在交易期根据信号进行交易

参考Gatev et al. (2006), Pairs trading: Performance of a relativevalue arbitrage rule
