# 11/04/2022
# Philip Boesch

import pandas as pd
import plotly.graph_objects as go 
# from compare_maic import df_copy

# import raw maic file for 1 time interval
filename = r'maic_raw/real_raw/third_test_inhuang/2020-01-01.txt'
df = pd.read_csv(filename, sep = '\t', header = 0)
score = 'maic_score'
df = df.sort_values(by = [score], ascending = False)


def get_categories(df_in):
	# get categories
	catsourcelist = df_in['contributors'].unique()
	df_incatdic = {}
	for s in catsourcelist:
		if(str(s)!="nan"):
			s = s.split(', ')
			for c in s:
				c = c.split(": ")
				df_incatdic[c[1]] = c[0]
	return df_incatdic

# obtain categories from the imported file
catdic = get_categories(df)
catcontents = {c:[] for c in catdic.values()}
catcontents[score] = [score]
for c in catdic:
	catcontents[catdic[c]].append(c)

outdic = {}

# create dataframe eith ctaegories as headers and genes as index
for index, row in df.iterrows():
	for c in catcontents.keys():
		outdic[row[df.columns[0]]] = {c:row[catcontents[c]].max() for c in catcontents.keys()}
outdf = pd.DataFrame(outdic).T


# drop everything but the top x genes (for convenience or whatever)
top = list(outdf[score].nlargest(n=10).index)
outdf = outdf[outdf.index.isin(top)]
headers = list(outdf.columns)
outdf = outdf.drop(columns = 'maic_score')

dfg = outdf.sum().sort_values(ascending=False).to_frame(name='2020-01-01')
dfg['bb'] = (dfg['2020-01-01'].divide(dfg['2020-01-01'].sum())) * 100



# for d in dsl:
#     c = df2[df2['contributors'].str.contains(d)]
#     datasets.at[d, "raw_contribution"] = c.sum()[d]
# datasets['contribution'] = datasets['raw_contribution'].divide(datasets['raw_contribution'].sum())
# datasets = datasets.sort_values(by=['contribution', 'rel_score'], ascending=False)

# create initial variables for sankey
labels = headers
sources = []
targets = []
values = []

# create dictionary for source information with the 'label' and the corresponding numeric source value
sourcedic = {headers[i] : i for i in range(0, len(headers))}

for index, row in dfg.iterrows():

# print(sources)
# set colours for links
color_link = ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']

# set colour for nodes
color_node = ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']

# plot the data
link = dict(source=sources, target=targets, value=values, color=color_link)
node = dict(label=labels, pad=35, thickness=10, color=color_node)
data = go.Sankey(link=link, node=node)



# print(catdic)
# print(catcontents)
# print(dfg)
# print(outdf

# print(sourcedic['PROTEOMICS'])
