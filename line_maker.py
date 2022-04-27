"""
09-03-2022
philip boesch
create line graph for genes
"""

import plotly.express as px
import pandas as pd
from compare_maic import df_copy, df_compare

# data = df_copy.iloc[:100]
data = df_copy.copy()
# top = df_compare['2022-01-01.txt'].nlargest(n=100)
# color_choice = 'custom_1'
# if color_choice == 'custom_1':
# 	colors = ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']

fig = px.scatter(
	data,
	title = "Change in MAIC rank on a 2-monthly basis - no_daniloski",
	template = 'plotly_white',
	# color_discrete_sequence = colors,
	labels = {
	"value" : "Rank Change",
	"variable" : "Date Interval",
	"gene" : "Gene ordered by final rank (01-03-2021)"
	}
	)

fig.update_layout(
	xaxis_showticklabels = False, xaxis_visible = True,
	font = dict(
		size = 20
		)
	)

fig.show()
# fig.write_image("/Users/philipboesch/Documents/Medicine/accpm_project/accpm_images/full_list_no_mick.png", width=2000, height=1236, scale=1)
