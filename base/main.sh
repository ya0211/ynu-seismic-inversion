#!/bin/bash

# SEED格式转SAC
python rdseed.py

# 合并数据（重命名）
python merge.py

# 添加事件
python eventinfo.py

# 去除仪器响应（去均值、去线性趋势和波形尖灭）
python transfer.py

# 分量旋转（数据裁窗）
python rotate.py

# 滤波
python filter.py

# 数据重采样
python resample.py
