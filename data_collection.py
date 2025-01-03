#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Injests Euroleague/Eurocup play-by-play data, box score data, and shot location data from euroleague_api package.
'E' for Euroleague, 'U' for Eurocup. 
Season = 2024 : '2024-2025 Season'
"""

# Imports 

import pandas as pd
import math
import numpy as np
import euroleague_api
from euroleague_api.shot_data import ShotData 
from euroleague_api.EuroLeagueData import EuroLeagueData
from euroleague_api.boxscore_data import BoxScoreData
from euroleague_api.play_by_play_data import PlayByPlay 
import random as rnd
from collections import Counter
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)

def get_euroleague_data(start_season: int, end_season: int):

   playbyplay = PlayByPlay(competition='E')
   playbyplay_data = playbyplay.get_game_play_by_play_data_multiple_seasons(start_season, end_season)
   
   shotdata = ShotData(competition='E')
   shot_data = shotdata.get_game_shot_data_multiple_seasons(start_season, end_season)
   
   boxdata = BoxScoreData(competition='E')
   boxscore_data = boxdata.get_player_boxscore_stats_multiple_seasons(start_season, end_season)
   
   return playbyplay_data, shot_data, boxscore_data


# In[ ]:




