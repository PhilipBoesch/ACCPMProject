# 14/03/2022
# Philip Boesch

import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 
from compare_maic import df_copy, top, bottom, top_july
df = df_copy.copy()

# select 100 genes that changed rank most
pos_change = df['2020-07-01'].nlargest(n=100).index
neg_change = df['2020-07-01'].nsmallest(n=100).index

choice = 'top'

if choice == 'bottom':
	c = bottom
if choice == 'top':
	c = top
if choice == 'pos':
	c = pos_change
if choice == 'neg':
	c = neg_change
if choice == 'top_july':
	c = top_july


df = df[df.index.isin(c)]

# create heatmap
# set size and dpi
plt.figure(
	figsize = (10, 35),
	dpi = 600
	)
sns.set(
	font_scale = 1.4)
# plot heatmap
ax = sns.heatmap(df,
	linewidths = 0.5,
	square = True,
	cbar_kws = {
	"shrink":1
	}
	)
# set title and labels
ax.set(
	title = "Change in rank of top 100 genes in July 2020 no_daniloski",
	ylabel = "Gene",
	xlabel = "Interval Date"
	)
ax.invert_yaxis()

# plt.show()
plt.savefig(r'test_image_no_daniloski.png')


# print(df)
