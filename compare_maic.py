#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 16:17:57 2022

@author: philipboesch
"""
import pandas as pd
import os
# =============================================================================
# let's compare maiiiaiaiaiaiaiaiaiaiiaiaiaiaiaiqic
# soooooooo, i could
# set the genes as the index and then just extract the maic_score - add this
# to a new column and then match it to the genes
# note; need to create a try loop to see if there is
# already a gene of that Name
# and if not then we need to add it to the index
# then, we need to compare the RANKING of the genes based on the maic score
# =============================================================================

# to run maic for all files in folder:
#     for file in /Users/philipboesch/Documents/Medicine/accpm_project/maic-master/input/*
# do python maic.py -f $file -o ./result

# done


path = r'maic_raw/no_pfef_raw'
maic_outputs = []
# for folder in os.listdir(path):
#     if not folder.startswith('.'):
#         old_file = os.listdir(path + '/' + folder)
#         old_file = ''.join(old_file)
#         old_file = r'maic_raw/no_pfef_raw/' + folder + '/' + old_file
#         destination = r'maic_raw/no_pfef_raw/newbie' + str(folder)
#         os.rename(old_file, destination)
    
    
        
# reading in all the files i want to compare from the 'path' folder
# also need to get rid of any hidden files (typically start with '.')
for item in os.listdir(path):
    if not item.startswith('.'):
        maic_outputs.append(item)

maic_outputs.sort()
fields = ['gene', 'maic_score']
# read maic scores into df
df_compare = pd.concat((pd.read_csv(r'maic_raw/no_pfef_raw/' + raw_file, sep='\t',
                                    index_col='gene',
                                    usecols=fields) for raw_file in maic_outputs),
                       axis=1)

# name columns after the maic output run
df_compare.set_axis(maic_outputs, axis=1, inplace=True)

# convert maic_score into a ranking where 1 = best
for col in df_compare:
    df_compare[col] = df_compare[col].rank(ascending=False)

# comparison = np.where(((df_compare["example1.txt"] - df_compare["example2.txt"]) > 100),True, False)

# df_compare['compare 1'] = np.where(((df_compare["example1.txt"] - df_compare["example2.txt"]) > 100),True, False)

# copying df in case i screw up
df_copy = df_compare.copy()

# df_copy
# df_copy['rank diff'] = (df_copy['2022-02-22--15-53.txt'] - df_copy['2022-02-22--15-52.txt'])

# I WILL FORMAT THIS NICELY LATER!
#
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

df_copy.to_excel(r'excel_stuff/no_pfef.xlsx')


# month to month is a bit meh until we have the landmark papers
# look for large changes over small periods of time
# have a look at every 2-3 months and see what it looks like
# us ethis to identify the landmark papers (ie the cirspr and gwas stuffs)
# then remove landmark papers 1 by 1 and see what happens to maic
# for the top genes: sankey diagram?
# look at how top genes changed etc
# colour by diff papes that had a big contribution
# i.e. do big papers with lots of info have an effect on skewing the reslults

# include heinrich hoffman!
