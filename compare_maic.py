#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 16:17:57 2022

@author: philipboesch
"""
import pandas as pd
import os

# to run maic for all files in folder:
# for file in /Users/philipboesch/Documents/Medicine/accpm_project/maic-master/input/*
# do python maic.py -f $file -o ./result/$file
# done

path = r'maic_raw/real_raw/full_input'
maic_outputs = []

# reading in all the files i want to compare from the 'path' folder
# also need to get rid of any hidden files (typically start with '.')
for item in os.listdir(path):
    if not item.startswith('.'):
        maic_outputs.append(item)

maic_outputs.sort()
fields = ['gene', 'maic_score']
# read maic scores into df
df_compare = pd.concat((pd.read_csv(r'maic_raw/real_raw/full_input/' + raw_file, sep='\t',
                                    index_col='gene',
                                    usecols=fields) for raw_file in maic_outputs),
                       axis=1)

# # name columns after the maic output run
df_compare.set_axis(maic_outputs, axis=1, inplace=True)

# # convert maic_score into a ranking where 1 = best
for col in df_compare:
    df_compare[col] = df_compare[col].rank(ascending=True)

df_compare = df_compare.sort_values(by = ['2022-01-01.txt'])

# copying df in case i screw up
df_copy = df_compare.copy()

# DOES THIS PART MAKE SENSE?
# for col in df_copy:
#     df_copy[col] = df_copy[col].nlargest(n=100)

# using .iloc to compare rank
interest = 0
first = 0
for column in df_copy:
    if interest == 0:
        interest += 1
        pass
    elif interest == 1:
        df_copy.insert(interest + 1, str(interest),
                       (df_copy.iloc[:, interest] - df_copy.iloc[:, first]))
        interest += 2
        first += 1
        pass
    else:
        df_copy.insert(interest + 1, str(interest),
                       (df_copy.iloc[:, interest] - df_copy.iloc[:, first]))
        interest += 2
        first += 2

df_copy.drop(list(df_copy.filter(regex = 'txt')), axis = 1, inplace = True)
# name columns after the maic output run
# remove one value as the comparison would b between 01 and 03 hence the first column will be from 03
maic_outputs.remove('2020-01-01.txt')
maic_outputs = [text.replace(".txt", '') for text in maic_outputs]
df_copy.set_axis(maic_outputs, axis=1, inplace=True)

# df_copy.to_excel(r'excel_stuff/2mo_full_test2.xlsx')


# month to month is a bit meh until we have the landmark papers
# look for large changes over small periods of time
# have a look at every 2-3 months and see what it looks like
# us ethis to identify the landmark papers (ie the cirspr and gwas stuffs)
# then remove landmark papers 1 by 1 and see what happens to maic
# for the top genes: sankey diagram?
# look at how top genes changed etc
# colour by diff papes that had a big contribution
# i.e. do big papers with lots of info have an effect on skewing the reslults
