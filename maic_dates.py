# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 14:49:52 2022

@author: philipboesch
"""
import os
import shutil
import pandas as pd
from crossref.restful import Works
from datetime import datetime, date, timedelta
# from file_compiler import compile_files
from dateutil.relativedelta import relativedelta
# read in MAIC excel sheet
raw_csv = pd.read_excel("accepted_gene_lists.xlsx")

raw_df = pd.DataFrame(raw_csv)
# raw_csv = raw_df - both dataframes, I just made a copy here

# Is study accepted into MAIC? -> dropping all rows with no maic input name
df_accepted = raw_df.dropna(subset=['Maic input name'])
# also need to drop some more due to 'DU' or 'NMOI' etc entries
df_accepted = df_accepted.drop(df_accepted[df_accepted["Maic input name"].isin(
    ["NMOI", "DU", "Not sure the data we need is available?",
     "Data Unavailable", "Data Unavaialble", "Re"])].index)

# creating a cell below this line
#%%
# automate date assignement
# setting crossref variable to make code less painful
works = Works()

# create new dict for pub date (value) and doi (key)
pub_dict = {}
# FOR loop for the above stuff to automate the process
for i in df_accepted['DOI']:
    d1 = works.doi(i)  # retrieve doi metadata as dict
    try:
        d2 = d1['published']  # select date of pub from doi metadata
    except TypeError:  # if problem in retrieval
        pub_date = 'do this manually'
        pub_dict[i] = pub_date
    else:
        d3 = d2['date-parts']  # extract str from dict
        d4 = (", ".join(repr(e) for e in d3))  # remove a set of []
        try:
            pub_date = datetime.strptime(d4, '[%Y, %m, %d]').date()
            pub_dict[i] = pub_date  # set and add pub date to new dict
        except (ValueError, TypeError):
            try:
                pub_date = datetime.strptime(d4, '[%Y, %m]').date()
                pub_dict[i] = pub_date
            except ValueError:  # in case no month is retrieved (ie year only)
                pub_date = 'do this manually'
                pub_dict[i] = pub_date
# creating a cell below this line
#%%
# identifying the dois of dates that need to be added manually
for key, ans in pub_dict.items():
    if ans == 'do this manually':
        print(key)
# creating a cell below this line
#%%
# adding the dates manually
pub_dict['10.1186/1471-2172-6-2'] = date.fromisoformat('2005-01-18')
pub_dict['10.1086/503843,16652313'] = date.fromisoformat('2006-06-01')
pub_dict['10.1016/j.immuni.2020.11.017.'] = date.fromisoformat('2020-12-15')
pub_dict['10.1128/JVI.00489-08,18632870'] = date.fromisoformat('2008-10-01')
# creating a cell below this line
#%%
# adding pub_dict to the main df as 'publication date'
df_final = df_accepted.copy()
df_final['Publication date'] = df_final['DOI'].map(pub_dict)
df_final['Publication date'] = pd.to_datetime(df_final['Publication date'])
df_final['Publication date'] = df_final['Publication date'].dt.date

# making the maic input names uniform by removing and adding '.txt'
df_final['Maic input name'] = df_final['Maic input name'].str.replace(
    '.txt', '', regex=True)
df_final['Maic input name'] = df_final['Maic input name'].str.replace(
    ',', '.txt,', regex=True)
df_final['Maic input name'] = df_final['Maic input name'].str.replace(
    ';', '.txt,', regex=True)
df_final['Maic input name'] = df_final['Maic input name'] + '.txt'


# function to retrieve dates and spit out maic inputs
def date_to_maic(low, high):
    """return maic inputs for specified dates between low and high (as str)"""
    mask = (df_final['Publication date'] > low) & \
        (df_final['Publication date'] <= high)
    m_input = df_final['Maic input name'].loc[mask]
    return m_input

#%%
#%%
def compile_files(files):
    """combine gene lists and create a combined maic input"""
    for file in files:
        # read all files and create a new file for the combined data
        try:
            with open('gene_lists/' + file, 'r') as in_file, open(
                    str(test_date) + '.txt', 'a') as out_file:
                col = ""  # setting the column variable to nothing
                for line in in_file:
                    # making data flat by removing \n
                    line = line.replace('\n', "")
                    # if the next line is blank but we still have lines left then
                    # we want to create a new row - ie if we've reached the end
                    # of the gene list for one study, we want to move on to the
                    # next study
                    if line == "" and len(col) > 0:
                        out_file.write(col + '\n')
                        col = ""
                    # if we still have stuff going on, then we want to seperate
                    # each gene with the '\t' seperator
                    else:
                        if len(col) > 0:
                            col += '\t'
                        col += line
                # as long as we have stuff to write - we want to write it
                # to the document
                if len(col) > 0:
                    out_file.write(col + '\n')
        except FileNotFoundError:
            print(file)  # prints out unmatched gene lists

path = r"gene_lists_copy"
path2 = r"no_daniloski"
os.mkdir(path2)

def folder_files(test_range):
    """combine gene lists into one folder to then be used to check the maic input formatting"""
    for date_obj in test_range:
        try:
            os.mkdir(path2 + '/' + str(test_date))
        except FileExistsError:
            pass
    for i in test_range:
        try:
            if not i.startswith('.'):
                shutil.copy(os.path.join(path, i), os.path.join(path2, str(test_date), i))
        except FileNotFoundError:
            print("File Not Found: " + i)


# start_date = datetime.date(2005, 1, 1)
# end_date = datetime.date(2022, 1, 1)
# delta = datetime.timedelta(months=1)

start_date = date(2005, 1, 1)  # set a start date for comparisons
test_date = date(2020, 1, 1)  # date up to which we compile
end_date = date(2022, 1, 1)  # final date compiled
delta = relativedelta(months=2)  # time increase between runs

# compile files between start date and test date, adding delta each time
while test_date <= end_date:
    folder_files(date_to_maic(start_date, test_date))
    test_date += delta

# =============================================================================
# Having a slight issue whereby some of the MAIC input names extracted from
# maic_corona_virus_data.xlsx do not match  or exist in the gene lists from
# the corona_maic folder. Some also provide more than one input name per study.
# perhaps a diff xl document?
# =============================================================================
# should i do <= or <
# lab meeting thurs: (write up)
# write code to compare the gene llists ranking by end of next week
# look if there are any other ways/mehtids of comparing gene ranking
# =============================================================================
# # list of questions and exact outputs you want to ask bo for maic
# to run maic - open terminal and input
# conda activate accpm_maic (vs conda deactivate)
# cd {file directory}
# python maic.py -f ./input/example.txt -o ./result

# to make pretty heatmaps and circular things
# python makeheatmap.py -f {} -o {} -r {}
# python circular_comparison.py -f {} -d {}
# remember input = results/maic_raw.txt
# for the maic heatmaps: run local server: python -m http.server
# ctrl c stops the server
# =============================================================================
