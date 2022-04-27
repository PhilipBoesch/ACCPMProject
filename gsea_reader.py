# 15/04/2022
# Philip Boesch

import numpy as np 
import pandas as pd 

filename = r'gsea_report4.tsv'
df = pd.read_csv(filename, sep = '\t')

data = np.where((df['NOM p-val'] < 0.01) & (df['FDR q-val'] < 0.25))

for i in data:
	print(df.iloc[i,1])