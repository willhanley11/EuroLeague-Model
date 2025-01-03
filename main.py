#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from data_collection import get_euroleague_data
from data_cleaning import clean_playbyplay_data

def main():
    playbyplay, shotdata, boxdata = get_euroleague_data(2022, 2024)
    cleaned_data = clean_playbyplay_data(playbyplay, boxdata, shotdata)

