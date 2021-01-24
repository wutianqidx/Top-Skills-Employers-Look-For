#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

data_dirs = ['data/Amazon_DS_Qualifications.txt', 'data/Amazon_RS_Qualifications.txt',
             'data/Amazon_ML_Qualifications.txt', 'data/Amazon_BI_Qualifications.txt',
             'data/Amazon_SDE_Qualifications.txt']

combined_data = None

for data_dir in data_dirs:
    data = pd.read_table(data_dir, sep = '\t')
    combined_data = pd.concat([combined_data, data])
    
combined_data = combined_data.reset_index(drop = True).dropna()
combined_data.to_csv('data/Amazon_Total_Qualifications.txt', sep = '\t', index = False)

