#!/usr/bin/env python
# coding: utf-8

# # Enrichr Manhattan Plot Creator
# 
# This appyter creates a figure visualizing enrichment analysis results from Enrichr (https://amp.pharm.mssm.edu/Enrichr/) in a manhattan plot. 
# 
# The resulting figure will contain a manhattan plot of the p-values of all the gene sets in the Enrichr libraries selected.

# In[2]:


import pandas as pd 
import math
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import numpy as np
import requests
import time
import bokeh.io
from operator import itemgetter
from IPython.display import display, FileLink, Markdown, HTML
from bokeh.plotting import ColumnDataSource, figure, output_notebook, show
from bokeh.models import Legend, LegendItem, Span
from matplotlib.pyplot import figure





# ### Input options

# In[35]:


gene_list_filename = ''
gene_list_input = '''MOV10
PABPC4
CXCL10
BCKDK
RTCB
UNC93B1
NMI
B2M
IFITM1
TRIM5
LGALS3
CD38
TGFB1
SPTLC2
IMPA2
SERPINE1
TNFRSF10A
ERBB3
CCHCR1
DTYMK
ZNF148
DLG1
SIRT3
RAB7A
RAB2A
TBK1
PABPC1
VPS39
STOM
IRF7
APOL1
EMC1
APOL6
RBX1
G3BP2
CSDE1
ACSL3
NPC2
IDE
RPS8
G3BP1
GNG5
EIF4H
TOR1A
CXCL11
UPF1
ETFA
ATP6AP1
DCAKD
CHMP2A
ALG5
RAB8A
HMOX1
TLR3
SUN2
SRP19
EXT1
NDUFB9
ALG11
EXOSC3
COLGALT1
VIM
FYCO1
CCL8
TBCA
CEP350
CFB
COQ8B
LAMP3
HDAC2
NGLY1
CSNK2B
PMPCB
IMPDH2
FAM162A
PSMD4
CEP43
PMPCA
FBLN5
GLA
TLE5
AGPS
TIMM10B
PVR
MTARC1
ADAM9
SLC30A7
MDN1
CCL2
EXTL3
SLC27A2
CLCC1
EDEM3
PKP2
PCNT
PRKACA
FAM20B
GGH
POR
NUP210
'''
transcription_libraries = []
pathways_libraries = ['KEGG_2019_Human', 'WikiPathways_2019_Human', 'BioPlanet_2019', 'Reactome_2016']    
ontologies_libraries = [] 
diseases_drugs_libraries = []
cell_types_libraries = []    
miscellaneous_libraries = []    
legacy_libraries = [] 
crowd_libraries = []
color_choice = 'custom_1'
significance_line = '4.60517018599'
legend_location = 'below'
label_location = 'right'
figure_file_format = ['png']
output_file_name = 'Enrichr_results_1'
final_output_file_names = [str(output_file_name+'.'+file_type) for file_type in figure_file_format]
enrichr_libraries = np.sort(transcription_libraries+pathways_libraries+ontologies_libraries+diseases_drugs_libraries+cell_types_libraries+miscellaneous_libraries+legacy_libraries+crowd_libraries)


# ### Import gene list

# In[36]:


# Import gene list as file or from text box file
# Will choose file upload over textbox if a file is given 
if gene_list_filename != '':
    open_gene_list_file = open(gene_list_filename,'r')
    lines = open_gene_list_file.readlines()
    genes = [x.strip() for x in lines]
    open_gene_list_file.close()
else:
    genes = gene_list_input.split('\n')
    genes = [x.strip() for x in genes]


# ### Get Enrichr Results
# 
# Enrichr is an open source web-based application for enrichment analysis and is freely available online at: http://amp.pharm.mssm.edu/Enrichr.

# In[37]:


# Function to get Enrichr Results
# Takes a gene list and Enrichr libraries as input
# Returns a dataframe containing gene sets and p-values
def Enrichr_API(enrichr_gene_list, all_libraries):

    for library_name in all_libraries : 
        ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/addList'
        genes_str = '\n'.join(enrichr_gene_list)
        description = 'Example gene list'
        payload = {
            'list': (None, genes_str),
            'description': (None, description)
        }

        response = requests.post(ENRICHR_URL, files=payload)
        if not response.ok:
            raise Exception('Error analyzing gene list')

        data = json.loads(response.text)
        time.sleep(0.5)
        ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/enrich'
        query_string = '?userListId=%s&backgroundType=%s'
        user_list_id = data['userListId']
        short_id = data["shortId"]
        gene_set_library = library_name
        response = requests.get(
            ENRICHR_URL + query_string % (user_list_id, gene_set_library)
         )
        if not response.ok:
            raise Exception('Error fetching enrichment results')

        data = json.loads(response.text)

        #results_df  = pd.DataFrame(data[library_name][0:5])
        
        results_df  = pd.DataFrame(data[library_name])
        # adds library name to the data frame so the libraries can be distinguished
        results_df['library'] = library_name.replace('_', '')


    return([results_df, str(short_id)])


# ### Assign Color Scheme

# In[38]:


colors = []

if color_choice == 'orange':
    colors = ['#FF5A00', '#FFA700', '#FF7400', '#FFDB00']
if color_choice == 'red/orange':
    colors = ['#FF0000',  '#FFCC00', '#FF6600', '#FF9800']
if color_choice == 'blue/purple':
    colors = ['#0000FF', '#A3A3FF', '#4949FF', '#7879FF']
if color_choice == 'green':
    colors = ['#2eb62c', '#abe098', '#57c84d', '#c5e8b7']
if color_choice == 'rainbow':
    colors = ['red', '#fef200', 'green', 'blue', 'purple']
if color_choice == 'blue/purple/orange':
    colors = ['#003f5c', '#7a5195', '#ef5675', '#ffa600']
if color_choice == 'purple/pink':
    colors = ['#9800b0', '#ef83bd', '#bc37b1', '#d95db5']
if color_choice == 'grayscale':
    colors = ['#000000', '#7a7a7a', '#3c3c3c', '#bdbdbd']
if color_choice == 'custom_1':
    colors = ['#332288', '#88CCEE', '#44AA99', '#117733']


# ### Plot Enrichr Results (static)

# In[39]:


# Function plots results 
def enrichr_figure():

    if len(enrichr_libraries) == 1:

        results_df = Enrichr_API(genes, enrichr_libraries)[0]

        all_terms = []
        all_pvalues = []

        all_terms.append(list(results_df[1]))
        all_pvalues.append(list(results_df[2]))

        # make a simple scatterplot
        fig, ax = plt.subplots(figsize=(10,4))

        # sort the elements alphabetically
        x=np.log10(all_pvalues[0])*-1
        sorted_terms = list(zip(all_terms[0], x))
        sorted_terms = sorted(sorted_terms, key = itemgetter(0))
        unzipped_sorted_list = list(zip(*sorted_terms))

        data = pd.DataFrame({"Gene Set": unzipped_sorted_list[0], "-log(p value)": unzipped_sorted_list[1]})

        # add significance line and label significant points
        if significance_line != '':
            ax.axes.axhline(y = float(significance_line), color = 'black', lw = 1)

            # label points above the significance line

            if label_location == 'right':
                coords = (6, -3)
            elif label_location == 'below':
                coords = (-3, -14)
            elif label_location == 'above':
                coords = (-4, 5)

            point_label = 1
            sig_point_handles = []
            for index, row in data.iterrows():
                if row["-log(p value)"] > float(significance_line):
                    ax.annotate(point_label, xy = (row["Gene Set"], row["-log(p value)"]), xytext = coords, textcoords='offset points')
                    actual_pvalue = "{:.5e}".format(10**(-1*row["-log(p value)"]))
                    sig_point_handles += [mpatches.Patch(color = 'white', label = str(point_label) + ": " + row["Gene Set"] + ", " + str(actual_pvalue))]
                    point_label += 1

            # create a legend for the significant points
            if point_label != 1:
                leg = plt.legend(handles = sig_point_handles, handlelength=0, handletextpad=0, loc='center left', bbox_to_anchor=(1, 0.5), title="Significant Points")
                ax.add_artist(leg)

        ax.scatter(unzipped_sorted_list[0], unzipped_sorted_list[1], color = colors[0])
        ax.axes.get_xaxis().set_ticks([])
        plt.ylabel("-log(p value)")
        plt.xlabel(enrichr_libraries[0])

    elif len(enrichr_libraries) > 1:
        # make a manhattan plot

        sorted_data = pd.DataFrame({"Gene Set": [], "-log(p value)": [], "Library": []})
        fig, ax = plt.subplots(figsize=(10,4))

        for i in range(len(enrichr_libraries)):
            # get enrichr results from the library selected
            results_df = Enrichr_API(genes, [enrichr_libraries[i]])[0]

            all_terms = []
            all_pvalues = []
            library_names = []

            all_terms.append(list(results_df[1]))
            all_pvalues.append(list(results_df[2]))
            library_names.append(list(results_df['library']))

            x=np.log10(all_pvalues[0])*-1
            sorted_terms = list(zip(all_terms[0], x, library_names[0]))
            sorted_terms = sorted(sorted_terms, key = itemgetter(0))
            unzipped_sorted_list = list(zip(*sorted_terms))

            data = pd.DataFrame({"Gene Set": unzipped_sorted_list[0], "-log(p value)": unzipped_sorted_list[1], "Library": unzipped_sorted_list[2]})
        
            sorted_data = pd.concat([sorted_data, data])

        # group data by library
        groups = sorted_data.groupby("Library")

        # plot points
        color_index = 0
        for name, group in groups:
            if color_index >= len(colors):
                color_index = 0
            plt.plot(group["Gene Set"], group["-log(p value)"], marker="o", linestyle="", label=name, color = colors[color_index])
            color_index += 1

        # remove labels and tick marks on the x-axis
        ax.axes.get_xaxis().set_ticks([])

        # now sort dataframe by p-value so the significant points are labeled in order
        sorted_pvalue_data = sorted_data.sort_values(by = ["-log(p value)"], ascending = False)

        # add significance line and label significant points
        if significance_line != '':
            ax.axes.axhline(y = float(significance_line), color = 'black', lw = 1)

            # label points above the significance line
            if label_location == 'right':
                coords = (6, -3)
            elif label_location == 'below':
                coords = (-3, -14)
            elif label_location == 'above':
                coords = (-4, 5)

            point_label = 1
            sig_point_handles = []
            for index, row in sorted_pvalue_data.iterrows():
                if row["-log(p value)"] > float(significance_line):
                    ax.annotate(point_label, xy = (row["Gene Set"], row["-log(p value)"]), xytext = coords, textcoords='offset points')
                    actual_pvalue = "{:.5e}".format(10**(-1*row["-log(p value)"]))
                    sig_point_handles += [mpatches.Patch(color = 'white', label = str(point_label) + ": " + row["Gene Set"] + ", " + str(actual_pvalue))]
                    point_label += 1

            # create a legend for the significant points
            if legend_location == 'side' and point_label != 1:
                leg = plt.legend(handles = sig_point_handles, handlelength=0, handletextpad=0, loc='center left', bbox_to_anchor=(1.5, 0.5), title="Significant Points")
                ax.add_artist(leg)
            elif point_label != 1:
                leg = plt.legend(handles = sig_point_handles, handlelength=0, handletextpad=0, loc='center left', bbox_to_anchor=(1, 0.5), title="Significant Points")
                ax.add_artist(leg)

        # adds a legend for the libraries in the location specified
        if legend_location == 'below':
            # shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                            box.width, box.height * 0.9])

            # put a legend below current axis
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                    fancybox=True, shadow=True, ncol=5)

        elif legend_location == 'side':
            # shrink current axis by 20%
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

            # put a legend to the right of the current axis
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        plt.ylabel("-log(p value)")

        # save results
    for plot_name in final_output_file_names:
        plt.savefig(plot_name, bbox_inches = 'tight')


    # plt.show()
    # plt.savefig('test1.png')
    if len(enrichr_libraries) > 1:
        return sorted_data, groups
    return data


# In[40]:


if len(enrichr_libraries) > 1:
    sorted_data, groups = enrichr_figure()
else:
    data = enrichr_figure()


# In[ ]:


# # download static plots
# for i, file in enumerate(final_output_file_names):
#     display(FileLink(file, result_html_prefix=str('Download ' + figure_file_format[i] + ': ')))


# ### Having trouble with overlapping point labels?
# Try moving the labels to a different location, plotting fewer libraries, or plot only one library at a time.

# ## Interactive plot using Bokeh

# In[15]:


# if len(enrichr_libraries) > 1:
#     # split data frame into smaller data frames by library
#     list_of_df = []
#     for library_name in enrichr_libraries:
#         library_name = library_name.replace('_', '')
#         df_new = sorted_data[sorted_data['Library'] == library_name]
#         list_of_df += [df_new]
# else:
#     list_of_df = [data]

# list_of_xaxis_values = []
# for df in list_of_df:  
#     list_of_xaxis_values += df["Gene Set"].values.tolist()

# # define the output figure and the features we want
# p = figure(x_range = list_of_xaxis_values, plot_height=300, plot_width=1000, tools='pan, box_zoom, hover, reset, save')

# # loop over all libraries
# r = []
# color_index = 0
# for df in list_of_df:
#     if color_index >= len(colors):
#         color_index = 0 

#     # calculate actual p value from -log(p value)
#     actual_pvalues = []
#     for log_value in df["-log(p value)"].values.tolist():
#         actual_pvalues += ["{:.5e}".format(10**(-1*log_value))]

#     # define ColumnDataSource with our data for this library
#     source = ColumnDataSource(data=dict(
#         x = df["Gene Set"].values.tolist(),
#         y = df["-log(p value)"].values.tolist(),
#         pvalue = actual_pvalues,
#     ))
    
#     # plot data from this library
#     r += [p.circle(x = 'x', y = 'y', size=5, fill_color=colors[color_index], line_color= colors[color_index], line_width=1, source = source)]
#     color_index += 1

# if len(enrichr_libraries) > 1:
#     # create custom legend for the libraries
#     color_index = 0
#     renderer_index = 0
#     legend_items = []
#     for library_name in enrichr_libraries:
#         legend_items += [LegendItem(label = library_name, renderers = [r[renderer_index]])]
#         renderer_index += 1

#     legend = Legend(items = legend_items, location = (0, 160))
#     p.add_layout(legend, 'right')

# # add significance line
# if significance_line != '':
#     hline = Span(location = float(significance_line), dimension='width', line_color='black', line_width=1)
#     p.renderers.extend([hline])

# p.background_fill_color = 'white'
# p.xaxis.major_tick_line_color = None 
# p.xaxis.major_label_text_font_size = '1pt'
# p.y_range.start = 0
# p.yaxis.axis_label = '-log(p value)'

# p.hover.tooltips = [
#     ("Gene Set", "@x"),
#     ("p value", "@pvalue"),
# ]

# p.output_backend = "svg"

# show(p)


# You can hover over the data points in this plot to see their associated gene set and p-value. Also check out the toolbar on the right side of the plot which will allow you to pan, box zoom, reset view, save the plot as an svg, and turn the hover display on/off.
