#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 14:49:52 2022

@author: philipboesch
"""

import pandas as pd
from crossref.restful import Works
from datetime import datetime
from datetime import date

# read in MAIC excel sheet
raw_csv = pd.read_excel("maic_corona_virus_data copy.xlsx")

raw_df = pd.DataFrame(raw_csv)
# raw_csv = raw_df - both dataframes, I just made a copy here in case i mess up

# Is study accepted into MAIC? -> dropping all rows with no maic input name
df_accepted = raw_df.dropna(subset=['Maic input name'])
# also need to drop some more due to 'DU' or 'NMOI' etc entries
df_accepted = df_accepted.drop(df_accepted[df_accepted["Maic input name"].isin(
    ["NMOI", "DU", "Not sure the data we need is available?",
     "Data Unavailable", "Data Unavaialble"])].index)

# creating a cell below this line
#%%
# create a fuction to automate date assignement...
# setting crossref variable to make code less painful
works = Works()

# create new dict for pub date and doi
pub_dict = {}
# FOR loop for the above stuff to automate the process
for i in df_accepted['DOI']:
    d1 = works.doi(i) #retrieve doi metadata as dict
    try:
        d2 = d1['published'] #select date of pub from doi metadata
    except TypeError: # if problem in retrieval
        pub_date = 'do this manually'
        pub_dict[i] = pub_date
    else:
        d3 = d2['date-parts'] # extract str from dict
        d4 = (", ".join( repr(o) for o in d3)) # remove a set of []
        try:
            pub_date = datetime.strptime(d4, '[%Y, %m, %d]').date()
            pub_dict[i] = pub_date #set and add pub date to new dict
        except (ValueError, TypeError):
            try:
                pub_date = datetime.strptime(d4, '[%Y, %m]').date()
                pub_dict[i] = pub_date
            except ValueError: # in case no month is retrieved (ie year only)
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
# creating a cell below this line
#%%
# adding pub_dict to the main df as 'publication date'
df_final = df_accepted
df_final['Publication date']=df_final['DOI'].astype(str).map(pub_dict)
#%%