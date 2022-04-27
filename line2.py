import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from compare_maic import df_compare

data = df_compare['2022-01-01.txt'].nlargest(n=20)
sns.heatmap(data)
plt.show()
# print(data)