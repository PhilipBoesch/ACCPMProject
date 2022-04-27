#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 16:17:57 2022

@author: philipboesch

compares all raw maic files in folder
"""
import pandas as pd
import os

# to run maic for all files in folder:
# for file in /Users/philipboesch/Documents/Medicine/accpm_project/maic-master/input/*
# do python maic.py -f $file -o ./result/$file
# done

path = r'maic_raw/real_raw/no_daniloski'
maic_outputs = []

# reading in all the files i want to compare from the 'path' folder
# also need to get rid of any hidden files (typically start with '.')
for item in os.listdir(path):
    if not item.startswith('.'):
        maic_outputs.append(item)

maic_outputs.sort()
fields = ['gene', 'maic_score']
# read maic scores into df
df_compare = pd.concat((pd.read_csv(
    r'maic_raw/real_raw/no_daniloski/' + raw_file, 
    sep='\t',
    index_col='gene',
    usecols=fields) for raw_file in maic_outputs), axis=1)

# name columns after the maic output run
df_compare.set_axis(maic_outputs, axis=1, inplace=True)
df_maic = df_compare.copy()
df_maic = df_maic.sort_values(by = ['2021-03-01.txt'])
# # convert maic_score into a ranking where 1 = lowest
# 24696 genes
for col in df_compare:
    df_compare[col] = df_compare[col].rank(ascending=True)

drop = df_compare['2021-03-01.txt'].nsmallest(n=21000)
top = df_compare['2021-03-01.txt'].nlargest(n=100).index
top_july = df_compare['2020-07-01.txt'].nlargest(n=100).index
bottom = df_compare['2021-03-01.txt'].nsmallest(n=100).index
df_compare = df_compare.sort_values(by = ['2021-03-01.txt'])
df_copy2 = df_compare.copy()

index_drop = drop.index
# df_compare.drop(index_drop, inplace = True)
# copying df in case i screw up
df_copy = df_compare.copy()


# DOES THIS PART MAKE SENSE?
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

# drop repeated time intervals with no new data - should fix in base code
drop_list = [
    '2021-05-01', 
    '2021-05-01', 
    '2021-07-01',
    '2021-09-01',
    '2021-11-01',
    '2022-01-01']
df_copy = df_copy.drop(columns = drop_list)

# print(df_copy.info())
# create enrichr input file (top 100 genes)

# with open('top_100_' + 'no_daniloski.txt', 'w') as out:
#     for i in top:
#         out.write(str(i) + '\n')
# # print(top)
# # df_copy.to_excel(r'excel_stuff/2mo_full_test2.xlsx')

# # write full gene list into tab deliminated file
# with open('full_' + 'no_daniloski.txt', 'w') as out_file:
#     for index, row in df_compare['2021-03-01.txt'].items():
#         out_file.write(str(index) + '\t' + str(row) + '\n')

# write gene list for tsv with maic score instead of rank

# with open(r'maic_' + 'no_daniloski.txt', 'w') as outf:
#     for index, row in df_maic['2021-03-01.txt'].items():
#         outf.write(str(index) + '\t' + str(row) + '\n')

# print(df_maic)

# month to month is a bit meh until we have the landmark papers
# look for large changes over small periods of time
# have a look at every 2-3 months and see what it looks like
# us ethis to identify the landmark papers (ie the cirspr and gwas stuffs)
# then remove landmark papers 1 by 1 and see what happens to maic
# for the top genes: sankey diagram?
# look at how top genes changed etc
# colour by diff papes that had a big contribution
# i.e. do big papers with lots of info have an effect on skewing the reslults
