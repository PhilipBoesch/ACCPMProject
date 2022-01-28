#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 14:49:52 2022

@author: philipboesch
"""

import pandas as pd
import numpy as np
from crossref.restful import Works
from datetime import datetime


#read in MAIC excel sheet
raw_csv = pd.read_excel("maic_corona_virus_data copy.xlsx")

raw_df = pd.DataFrame(raw_csv)
#raw_csv = raw_df - both dataframes, I just made a copy here in case i mess up

#Is study accepted into MAIC? -> dropping all rows with no maic input name
# could have decided which were accepted numerouis ways - thought this would 
# make the most sense since i need to run this col through maic anyway
df_accepted = raw_df.dropna(subset=['Maic input name'])
#also need to drop some more due to 'DU' or 'NMOI' etc entries - 
#also typos dont help - noticed some quite late - 
#in future: standardise either yes or no to save this type of hassle and error
# managebale here, but if we have like 300000 studies it could be painful
df_accepted = df_accepted.drop(df_accepted[df_accepted["Maic input name"].isin(
    ["NMOI", "DU", "Not sure the data we need is available?",
     "Data Unavailable", "Data Unavaialble"])].index)



#setting crossref variable to make code less painful
works = Works()
#retrieve doi metadata as dict - somehow doesnt come out as json?!
# despite documents saying otherwise
w1 = works.doi('10.1007/s12250-015-3581-8')
#selecting the date of publishing from the above doi
# in future could just add the puyblishing date to the main file in the first
# place - tales up one column and is very useful for retrospective studies
w2 = w1['published']
w3 = w2['date-parts']
#removing a set of square brackets to create str from list
w4 = (", ".join( repr(e) for e in w3))
#converting str into date
datetime_object = datetime.strptime(w4, '[%Y, %m, %d]').date()

for i in df_accepted['DOI']:
    d1 = works.doi(i)
    d2 = d1['published']
    d3 = d2['date-parts']
    d4 = (", ".join( repr(o) for o in d3))
    pub_date = datetime.strptime(d4, '[%Y, %m, %d]').date()
    #set the new column to the date here
    
    
    
    
# 10.1007/s12250-015-3581-8 was on 17th - errorssssssss :( 
# don't know how to fix

#set length of new date column
l = len(df_accepted['DOI'])
#create new column named 'publication date' and set 'type' to datetime
#need to look into getting rid of time  itself here here
df_accepted['Publication date'] = pd.to_datetime(df_accepted['Publication date'], format='%d/%m/%Y')
# create a fuction to automate date assignement, and add 
#the date to the new column

