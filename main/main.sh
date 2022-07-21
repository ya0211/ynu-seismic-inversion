#!/bin/bash

# SEED格式转SAC
python rdseed.py -s ../data -o data -S SAC -P SAC_PZs

# 合并数据（重命名）
python merge.py -S data/SAC -r

# 添加事件
python eventinfo.py -S data/SAC -i  data/CMTSOLUTION.json

# 去除仪器响应（去均值、去线性趋势和波形尖灭）
python transfer.py -S data/SAC -P data/SAC_PZs -TS 0.5 -TL 100.0 -r

# 分量旋转（数据裁窗）
python rotate.py -S data/SAC -N SAC-N

# 数据重采样
python resample.py -S data/SAC-N