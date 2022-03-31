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

fig = px.scatter(
	data,
	title = "Change in MAIC rank on a 2-monthly basis - TEST",
	template = 'plotly_white',
	labels = {
	"value" : "Negative Rank Change",
	"variable" : "Date",
	"gene" : "Gene"
	}
	)

fig.update_layout(
	font = dict(
		size = 20
		)
	)

# fig.show()
fig.write_image("/Users/philipboesch/Documents/Medicine/accpm_project/accpm_images/TEST1.png", width=2000, height=1236, scale=1)
