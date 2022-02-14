#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 09:35:45 2022

@author: philipboesch
"""

import numpy as np
import seaborn as sns
import matplotlib.pylab as plt

data = np.random.rand(10,12)

# using seaborn 
a = sns.heatmap(data)

# using matplotlib
b = plt.imshow(data, cmap = 'RdBu', interpolation = 'nearest')
