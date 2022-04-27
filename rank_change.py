# 15/03/2022
# Philip Boesch
'''multi-purpose file for minor functions needed as and when needed'''

# import os
# import pandas as pd
# from compare_maic import df_copy, top, bottom, top_july


# filename = r'maic_raw/real_raw/third_test_inhuang/2021-03-01.txt'
# df = pd.read_csv(filename, sep = '\t', header = 0)
# score = 'maic_score'
# top = list(df[score].nlargest(n=100).index)
# df = df[df.index.isin(top)]

# df.to_csv(r'top100_circ.txt', sep = '\t')



# length of gene lists in folder
# s = r'maic_inputs/third_test_inhuang/2020-07-01/'
# source = os.listdir(r'maic_inputs/third_test_inhuang/2020-07-01')
# l_lengths = []

# for file in source:
# 	if not file.startswith('MAIC'):
# 		with open(s + file, 'r') as in_file:
# 			l = len(in_file.readlines()) - 4
# 			l_lengths.append(l)

# print(l_lengths)


# with open(r'matched_1.txt', 'a') as out:
# 	for i in top:
# 		if i in top_july:
# 			out.write(i + ', ')

# data = []

# for i in top:
# 	if i in top_july:
# 		data.append(i)

# print(len(data))


# for col in df_copy:
# 	i = df_copy[col].nsmallest(n=100)
# 	data.append(i)

# print(data)


# with open('test1.txt', 'a') as out:
# 	for col in df_copy:
# 		i = df_copy[col].nlargest(n=100)
# 		out.write(str(i))
