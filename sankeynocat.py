# 11/04/2022
# Philip Boesch

import os
import pandas as pd
import plotly.graph_objects as go 
from compare_maic import df_copy, df_copy2

df = df_copy2

# fpath = r'maic_raw/real_raw/third_test_inhuang'

top = list(df['2021-03-01.txt'].nlargest(n=10).index)
df = df[df.index.isin(top)]
drop_list = [
    '2021-05-01.txt', 
    '2021-05-01.txt', 
    '2021-07-01.txt',
    '2021-09-01.txt',
    '2021-11-01.txt',
    '2022-01-01.txt']
df = df.drop(columns = drop_list)


labels = top
sources = []
targets = []
values = []

# source:
sourcedic = { top[i] : i for i in range(0, len(top) ) }

# def sourcing(interval):
# 	for row in interval:
# 		if row.isnull() == True:
# 			pass
# 		else:
# 			sources.append(row)

# sourcing(df['2020-07-01.txt'])



print(sourcedic)