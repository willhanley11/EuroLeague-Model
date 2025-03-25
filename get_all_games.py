#!/usr/bin/env python
# coding: utf-8

# Euroleague/Eurocup player driven game simulator

# In[2]:


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
import os
import pickle
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)

import warnings
warnings.filterwarnings('ignore')

def get_euroleague_data(start_season: int, end_season: int):

   playbyplay = PlayByPlay(competition='E')
   playbyplay_data = playbyplay.get_game_play_by_play_data_multiple_seasons(start_season, end_season)
   
   shotdata = ShotData(competition='E')
   shot_data = shotdata.get_game_shot_data_multiple_seasons(start_season, end_season)
   
   boxdata = BoxScoreData(competition='E')
   boxscore_data = boxdata.get_player_boxscore_stats_multiple_seasons(start_season, end_season)
   
   return playbyplay_data, shot_data, boxscore_data

playbyplay, shotdata, boxscore = get_euroleague_data(2024,2024)


# In[3]:


playbyplay.head()


# In[4]:


def clean_playbyplay_data(playbyplay, boxdata, shotdata):
    
    """
    Cleans and amplifies euroleague_api play-by-play data by:
    - Merging shot data and relevant boxscore data with play-by-play
    - Identifying players on the court at each moment of each game
    - Finds and addresses inconsistencies
    - Identifies and fixes potential errors
    - Breaks down start and finish of each possession
    - Eliminates garbage time possessions
    
    Args:
        playbyplay_data: Raw play-by-play data
        boxscore_data: Raw boxscore data
        shot_data: Raw shot location data
        
    Returns:
        pd.DataFrame: Clean and consistent play-by-play dataset
        
    """

    # Get initial players on the court via boxscore and merge with Play by Play
    startershome = boxdata[(boxdata['IsStarter'] == 1) & (boxdata['Home'] == 1)]
    startersaway = boxdata[(boxdata['IsStarter'] == 1) & (boxdata['Home'] == 0)]
    
    df1 = startershome.groupby(["Season", "Gamecode"]).agg({"Player_ID": lambda x: [str(item).strip() for item in x.unique().tolist()]}).reset_index()
    df1['HomePlayersOnCourt'] = df1['Player_ID']
    df1 = df1[['Season','Gamecode','HomePlayersOnCourt']]
    
    df2 = startersaway.groupby(["Season", "Gamecode"]).agg({"Player_ID": lambda x: [str(item).strip() for item in x.unique().tolist()]}).reset_index()
    df2['AwayPlayersOnCourt'] = df2['Player_ID']
    df2 = df2[['Season','Gamecode','AwayPlayersOnCourt']]
    
    home = boxdata[boxdata['Home'] == 1]
    home.loc[:, 'HomeTeam'] = home['Team']
    home = home[['Season','Gamecode','HomeTeam']].drop_duplicates()
    away = boxdata[boxdata['Home'] == 0]
    away.loc[:, 'AwayTeam'] = away['Team']
    away = away[['Season','Gamecode','AwayTeam']].drop_duplicates()
    
    teams = pd.merge(home,away,left_on=['Season','Gamecode'],right_on=['Season','Gamecode'])
    starters = pd.merge(df1,df2, left_on=['Season','Gamecode'],right_on=['Season','Gamecode'])
    starters['PERIOD'] = 1
    starters['PLAYINFO'] = 'Begin Period'
    
    playbyplay.drop_duplicates(inplace=True)
    
    playbyplay2 = pd.merge(playbyplay,starters, left_on=['Season','Gamecode','PLAYINFO','PERIOD'],right_on=['Season','Gamecode','PLAYINFO','PERIOD'], how='left')
    
    
    # Merge shot data with new play by play (including starters)
    alldata = pd.merge(playbyplay2, shotdata, left_on=['Season','Gamecode','NUMBEROFPLAY'], right_on=['Season','Gamecode','NUM_ANOT'], how='left')
    
    alldata = pd.merge(alldata,teams,left_on=['Season','Gamecode'],right_on=['Season','Gamecode'])
    
    
    # Preproccessing and Cleaning of Play by Play
    alldata['PLAYTYPE'] = alldata['PLAYTYPE'].str.strip()
    
    alldata['PLAYTYPE'] = np.where(alldata['PLAYTYPE'] == '2FGAB','2FGA',alldata['PLAYTYPE'])
    alldata['PLAYTYPE'] = np.where(alldata['PLAYTYPE'] == '3FGAB','3FGA',alldata['PLAYTYPE'])
    
    
    
    # Add game minute and seconds elapsed columns
    def fill_marker_time(row):
        if pd.isna(row['MARKERTIME']) or row['MARKERTIME'] == '':
            if row['PLAYTYPE'] == 'BP':
                return '10:00'
            elif row['PLAYTYPE'] in ['EP', 'EG']:
                return '00:00'
        return row['MARKERTIME']
    
    def calculate_marker_time(row):
        if row['MARKERTIME'] == 'ND':
            minute_x = row['MINUTE_x']
            if row['PERIOD'] == 1:
                return f"{10 - minute_x}:00"
            elif row['PERIOD'] == 2:
                return f"{20 - minute_x}:00"
            elif row['PERIOD'] == 3:
                return f"{30 - minute_x}:00"
            elif row['PERIOD'] == 4:
                return f"{40 - minute_x}:00"
        return row['MARKERTIME']
    
    alldata['MARKERTIME'] = alldata.apply(calculate_marker_time, axis=1)
    
    alldata['MARKERTIME'] = alldata.apply(fill_marker_time, axis=1)
    
    def time_to_seconds_elapsed(time_str):
        minutes, seconds = map(int, time_str.split(':'))
        total_seconds = minutes * 60 + seconds
        elapsed_seconds = 600 - total_seconds
        return elapsed_seconds
    
    alldata['PeriodSecondsElapsed'] = alldata['MARKERTIME'].apply(time_to_seconds_elapsed)
    
    alldata['NumberOfPlay'] = alldata.groupby(['Season', 'Gamecode']).cumcount() + 1
    
    
    # Iterate through all games and use subsitution rows from play by play to find players on the court for each event
    home_starters = []
    current_gamecode = None
    for index, row in alldata.iterrows():
        if current_gamecode != row['Gamecode']:
            # Initialize home_starters with the current HomePlayersOnCourt
            home_starters = row['HomePlayersOnCourt'] if isinstance(row['HomePlayersOnCourt'], list) else []
            current_gamecode = row['Gamecode']
        elif row['PLAYINFO'] == 'In' and row['CODETEAM'] == row['HomeTeam']:
            home_starters.append(row['PLAYER_ID'])
        elif row['PLAYINFO'] == 'Out' and row['CODETEAM'] == row['HomeTeam']:
            if row['PLAYER_ID'] in home_starters:
                home_starters.remove(row['PLAYER_ID'])
        alldata.at[index, 'HomePlayersOnCourt'] = home_starters.copy() if home_starters else None
    away_starters = []
    current_gamecode = None
    for index, row in alldata.iterrows():
        if current_gamecode != row['Gamecode']:
            # Initialize away_starters with the current AwayPlayersOnCourt
            away_starters = row['AwayPlayersOnCourt'] if isinstance(row['AwayPlayersOnCourt'], list) else []
            current_gamecode = row['Gamecode']
        elif row['PLAYINFO'] == 'In' and row['CODETEAM'] == row['AwayTeam']:
            away_starters.append(row['PLAYER_ID'])
        elif row['PLAYINFO'] == 'Out' and row['CODETEAM'] == row['AwayTeam']:
            if row['PLAYER_ID'] in away_starters:
                away_starters.remove(row['PLAYER_ID'])
        alldata.at[index, 'AwayPlayersOnCourt'] = away_starters.copy() if away_starters else None
    
    
    
    # Remove non wanted events (technical fouls, substitutions, challanges, timeouts, tipoffs, etc), no OT
    alldata = alldata[~alldata['PLAYTYPE'].isin(['TPOFF','IN','OUT','TOUT','F','RV','BF',
                                                             'AG','TOUT_TV','CCH'])].sort_values(by=['Season','Gamecode',
                                                                                                   'NumberOfPlay'], ascending=[True,True,True])
    alldata = alldata[(alldata['PERIOD']).isin([1,2,3,4])]
    
    alldata = alldata[~(alldata['PLAYTYPE']).isin(['TPOFF','JB'])]
    print("2")
    
    # Fix errors in play by play
    alldata['CODETEAM'] = np.where(
        (alldata['PLAYTYPE'] == 'BP') & (~alldata['PLAYTYPE'].shift(-1).isin(['CM','FV','C','CMT','CMU'])),
        alldata['CODETEAM'].shift(-1),
        np.where(
            (alldata['PLAYTYPE'] == 'BP') & (~alldata['PLAYTYPE'].shift(-2).isin(['CM','FV','C','CMT','CMU'])),
            alldata['CODETEAM'].shift(-2),
            np.where(
                (alldata['PLAYTYPE'] == 'BP') & (~alldata['PLAYTYPE'].shift(-3).isin(['CM','FV','C','CMT','CMU'])),
                alldata['CODETEAM'].shift(-3),
                alldata['CODETEAM'] ) ))
    
    alldata['PLAYTYPE'] = np.where(
        (alldata['PLAYTYPE'] == 'O') & 
        (alldata['PLAYTYPE'].shift(1).isin(['2FGA', '3FGA', 'FTA'])) & 
        (alldata['CODETEAM'].shift(1) != alldata['CODETEAM']),
        'D',
        np.where(
            (alldata['PLAYTYPE'] == 'D') & 
            (alldata['PLAYTYPE'].shift(1).isin(['2FGA', '3FGA', 'FTA'])) & 
            (alldata['CODETEAM'].shift(1) == alldata['CODETEAM']),
            'O',
            np.where(
                (alldata['PLAYTYPE'] == 'O') & 
                (alldata['PLAYTYPE'].shift(2).isin(['2FGA', '3FGA', 'FTA'])) & 
                (alldata['PLAYTYPE'].shift(1) == 'FV') & 
                (alldata['CODETEAM'].shift(1) == alldata['CODETEAM']),
                'D',
                alldata['PLAYTYPE'] )   ))
    
    alldata['Next_PLAYTYPE_1'] = alldata['PLAYTYPE'].shift(-1)
    alldata['Next_PLAYTYPE_2'] = alldata['PLAYTYPE'].shift(-2)
    alldata['Next_PLAYTYPE_3'] = alldata['PLAYTYPE'].shift(-3)
    alldata['Next_PLAYTYPE_4'] = alldata['PLAYTYPE'].shift(-4)
    
    alldata['Next_Teamcode_1'] = alldata['CODETEAM'].shift(-1)
    alldata['Next_Teamcode_2'] = alldata['CODETEAM'].shift(-2)
    alldata['Next_Teamcode_3'] = alldata['CODETEAM'].shift(-3)
    alldata['Next_Teamcode_4'] = alldata['CODETEAM'].shift(-4)
    
    
    alldata['LastPossessionOfQuarter'] = 0
    alldata['LastPossessionOfQuarter'] = (alldata['Next_PLAYTYPE_1'].isin(['EP','EG'])).astype(int)
    
    alldata['MissedFTDreb'] = 0
    alldata['MissedFTDreb'] = ((alldata['PLAYTYPE'] == 'FTA') & 
                        (alldata['Next_PLAYTYPE_1'] == 'D')).astype(int)
    
    alldata['MissedFTOreb'] = 0
    alldata['MissedFTOreb'] = ((alldata['PLAYTYPE'] == 'FTA') & 
                        (alldata['Next_PLAYTYPE_1'] == 'O')).astype(int)
    
    alldata['techFT'] = np.where(
        ((alldata['PLAYTYPE'].isin(['FTA', 'FTM'])) & (alldata['PLAYTYPE'].shift(1).isin(['C', 'CMT','CMTI','B']))),1,0)
    
    alldata['UnsportsFT'] = np.where(((alldata['PLAYTYPE']).isin(['FTA','FTM'])) & 
                                    ((alldata['PLAYTYPE'].shift(1).isin(['CMU','CMD'])) | 
                                     (alldata['PLAYTYPE'].shift(2).isin(['CMU', 'CMD','CMT'])) |
                                     (alldata['PLAYTYPE'].shift(3).isin(['CMU', 'CMD',]))),1,0)
    
    alldata['And1'] = (
        ((alldata['PLAYTYPE'].isin(['2FGM', '3FGM'])) & 
                        (alldata['Next_PLAYTYPE_1'] == 'CM') & ((alldata['Next_PLAYTYPE_2']).isin(['FTA','FTM'])) &
                        (alldata['CODETEAM'] == alldata['Next_Teamcode_2']))|
        ((alldata['PLAYTYPE'].isin(['2FGM', '3FGM'])) & 
                        (alldata['Next_PLAYTYPE_1'] == 'AS') & ((alldata['Next_PLAYTYPE_2']).isin(['CM'])) &
                        (alldata['CODETEAM'] != alldata['Next_Teamcode_2']) &
                        (alldata['PLAYER_ID'] == alldata['PLAYER_ID'].shift(-3))) |
        ((alldata['PLAYTYPE'].isin(['2FGM', '3FGM'])) & 
                        (alldata['Next_PLAYTYPE_1'] == 'CM') & ((alldata['Next_PLAYTYPE_2']).isin(['AS'])) &
                        (alldata['CODETEAM'] == alldata['Next_Teamcode_3']) &
                        (alldata['Next_PLAYTYPE_3'].isin(['FTA','FTM'])))).astype(int)
    
    alldata['AssistedBasket'] = np.where(((alldata['PLAYTYPE']).isin(['2FGM','3FGM','FTM'])) & (alldata['Next_PLAYTYPE_1'] == 'AS'),1,0)
    
    alldata['UnsportsBasket'] = np.where(((alldata['PLAYTYPE']).isin(['2FGM','3FGM','FTM'])) & (alldata['Next_PLAYTYPE_1'] == 'CMU')
                                         & (alldata['PeriodSecondsElapsed'] == alldata['PeriodSecondsElapsed'].shift(-1))
                                         & (alldata['CODETEAM'] != alldata['Next_Teamcode_1']),1,0)
    
    alldata['OFFnotTO'] = np.where(((alldata['PLAYTYPE']).isin(['OF'])) & (alldata['Next_PLAYTYPE_1'] != 'TO'),1,0)
    
    alldata['TOSteal'] = np.where(((alldata['PLAYTYPE']).isin(['TO'])) & (alldata['Next_PLAYTYPE_1'] == 'ST'),1,0)
    
    alldata['StealTO'] = np.where(((alldata['PLAYTYPE']).isin(['ST'])) & (alldata['Next_PLAYTYPE_1'] == 'TO')&
                                  (alldata['CODETEAM'] != alldata['Next_Teamcode_1']),1,0)
    
    alldata['POTENTIALERROR'] = np.where(
        (  ( (alldata['PLAYTYPE'].isin(['2FGA', '3FGA']) & (~alldata['PLAYTYPE'].shift(-1).isin(['O', 'D', 'EP', 'EG', 'BP', 'FV','CM']))) |
                (alldata['PLAYTYPE'].isin(['AS']) & (alldata['PLAYTYPE'].shift(1).isin(['2FGA', '3FGA']))) |
                (alldata['PLAYTYPE'].isin(['2FGM', '3FGM']) & (alldata['PLAYTYPE'].shift(-1).isin(['O', 'D'])))  ) & ~(
                (alldata['PLAYTYPE'].isin(['2FGA', '3FGA']) & 
                 (alldata['PLAYTYPE'].shift(-1) == 'TO') & 
                 (alldata['CODETEAM'] == alldata['CODETEAM'].shift(-1)))  ) ),  1,  0)
    
    alldata['POTENTIALERROR2'] = np.where((alldata['PLAYTYPE'] == alldata['PLAYTYPE'].shift(-1)) & (alldata['PLAYER_ID'] == alldata['PLAYER_ID'].shift(-1))
                                          & (alldata['PeriodSecondsElapsed'] == alldata['PeriodSecondsElapsed'].shift(-1)) 
                                          &(~alldata['PLAYTYPE'].isin(['FTA','FTM'])), 1,0)
    
    alldata['POTENTIALERROR3'] = np.where(
        (alldata['PLAYTYPE'].str.contains('FGA')) &  
        (alldata['PLAYTYPE'].shift(-1).str.contains('FGA')) &  
        (alldata['CODETEAM'] == alldata['CODETEAM'].shift(-1)) &  
        (alldata['PLAYTYPE'].shift(-2) == 'O') &  
        (alldata['CODETEAM'] == alldata['CODETEAM'].shift(-2)),1,0)
    
    alldata['Temp_FoulOffBall'] = np.where(
        (alldata['PLAYTYPE'].isin(['AS', '2FGM', '3FGM'])) & 
        (alldata['Next_PLAYTYPE_1'].isin(['CM'])) & (alldata['Next_Teamcode_1'] != alldata['CODETEAM']) &
        (~alldata['Next_PLAYTYPE_2'].isin(['CM', 'FV', 'CMT', 'FTA', 'FTM'])) & 
        (alldata['Next_Teamcode_2'] == alldata['CODETEAM']),  1,  0)
    
    alldata['FoulOffBall'] = np.where(
        (alldata['PLAYTYPE'] == 'CM') & 
        (alldata['Temp_FoulOffBall'].shift(1) == 1) & ((alldata['PLAYTYPE']).shift(-1) == 'AS'),  1,  alldata['Temp_FoulOffBall'])
    
    alldata.drop(columns=['Temp_FoulOffBall'], inplace=True)
    
    
    
    # Account for FT Events
    ft_data = alldata[((alldata['PLAYTYPE'] == 'FTA') | (alldata['PLAYTYPE'] == 'FTM')) & ((alldata['techFT'] == 0) & (alldata['UnsportsFT'] == 0))]
    
    ft_data = ft_data.groupby(by=['Season','CODETEAM','Gamecode',
                                 'PERIOD','MARKERTIME',]).agg({'NumberOfPlay':'max',}).reset_index()
    ft_data['Last_FT1'] = 1
    
    alldata = pd.merge(alldata,ft_data, left_on=['Season','CODETEAM','Gamecode','PERIOD','MARKERTIME','NumberOfPlay'],
            right_on=['Season','CODETEAM','Gamecode','PERIOD','MARKERTIME','NumberOfPlay'],how='left')
    
    alldata['Last_FT'] = np.where((alldata['Last_FT1'] == 1) & (alldata['Last_FT1'].shift(-1) == 1),0,alldata['Last_FT1'])
    
    alldata['FirstFTAst'] = np.where(((alldata['PLAYTYPE']).isin(['AS'])) & ((alldata['PLAYTYPE']).shift(1) == 'FTM')
                                & ((alldata['Last_FT']).shift(1) != 1),1,0)
    
    alldata['LastFTMissedAst'] = np.where(((alldata['PLAYTYPE']).isin(['AS'])) & ((alldata['PLAYTYPE']).shift(1) == 'FTA')
                                          & ((alldata['PLAYTYPE']).shift(2) == 'FTM') & (((alldata['PLAYTYPE']).shift(-1)).isin(['O','D']))
                                & ((alldata['Last_FT']).shift(1) == 1),1,0)
    
    alldata['And1Assisted'] = np.where(((alldata['PLAYTYPE'] == 'AS') & ((alldata['And1']).shift(1) == 1)) |
                                       ((alldata['PLAYTYPE'] == 'AS') & ((alldata['And1']).shift(2) == 1)
                                       &(alldata['PLAYTYPE'].shift(1) == 'CM')),1,0)
    
    alldata['Last_FTError'] = np.where((alldata['Last_FT'] == 1) & (alldata['PLAYTYPE'] == 'FTA') & (~alldata['PLAYTYPE'].shift(-1).isin(['O', 'D'])),1,0)
    
    print("3")
    
    # Number possessions for home and away teams
    home_possessions = 0
    away_possessions = 0
    current_possession_team = None
    current_game_id = None
    
    for index, row in alldata.iterrows():
        game_id = (row['Season'], row['Gamecode'])  
        if game_id != current_game_id:
            current_game_id = game_id
            home_possessions = 0
            away_possessions = 0
            current_possession_team = None
        if row['PLAYTYPE'] == 'BP' and row['PERIOD'] == 1: 
            if row['CODETEAM'] == row['HomeTeam']:
                current_possession_team = 'HomeTeam'
                home_possessions = 1
            else:
                current_possession_team = 'AwayTeam'
                away_possessions = 1      
        if row['LastPossessionOfQuarter'] == 1:
            pass
        elif row['POTENTIALERROR2'] == 1:
            pass
        elif row['POTENTIALERROR3'] == 1:
            pass
        elif row['FoulOffBall'] == 1:
            pass
        elif row['StealTO'] == 1:
            pass
        elif row['UnsportsBasket'] == 1:
            pass
        elif row['LastFTMissedAst'] == 1:
            pass
        elif ((row['PLAYTYPE'] in ['2FGM','3FGM','FTM']) & (row['AssistedBasket'] == 1)):
            pass
        elif ((row['PLAYTYPE'] in ['2FGM', '3FGM']) & (row['And1'] == 0) & (row['AssistedBasket'] == 0)):
            if current_possession_team == 'HomeTeam':
                away_possessions += 1
                current_possession_team = 'AwayTeam'
            else:
                home_possessions += 1
                current_possession_team = 'HomeTeam'
        elif ((row['PLAYTYPE'] in ['FTA','FTM']) & (row['MissedFTOreb'] == 1)):
            pass
        elif ((row['PLAYTYPE'] == 'FTM')  & (row['AssistedBasket'] == 0) & (row['Last_FT'] == 1)):
            if current_possession_team == 'HomeTeam':
                away_possessions += 1
                current_possession_team = 'AwayTeam'
            else:
                home_possessions += 1
                current_possession_team = 'HomeTeam'
        elif row['POTENTIALERROR'] == 1:
            if current_possession_team == 'HomeTeam':
                away_possessions += 1
                current_possession_team = 'AwayTeam'
            else:
                home_possessions += 1
                current_possession_team = 'HomeTeam'
        elif row['Last_FTError'] == 1:
            if current_possession_team == 'HomeTeam':
                away_possessions += 1
                current_possession_team = 'AwayTeam'
            else:
                home_possessions += 1
                current_possession_team = 'HomeTeam'
        elif row['OFFnotTO'] == 1:
            if current_possession_team == 'HomeTeam':
                away_possessions += 1
                current_possession_team = 'AwayTeam'
            else:
                home_possessions += 1
                current_possession_team = 'HomeTeam'
        elif row['PLAYTYPE'] == 'D':
            if current_possession_team == 'HomeTeam':
                away_possessions += 1
                current_possession_team = 'AwayTeam'
            else:
                home_possessions += 1
                current_possession_team = 'HomeTeam'
        elif row['PLAYTYPE'] == 'OF':
            if current_possession_team == 'HomeTeam':
                current_possession_team = 'HomeTeam'
            else:
                current_possession_team = 'AwayTeam'
        elif (row['PLAYTYPE'] == 'TO') and (row['TOSteal'] == 0):
            if current_possession_team == 'HomeTeam':
                away_possessions += 1
                current_possession_team = 'AwayTeam'
            else:
                home_possessions += 1
                current_possession_team = 'HomeTeam'
        elif row['FirstFTAst'] == 1:
            pass
        elif row['And1Assisted'] == 1:
            pass
        elif row['PLAYTYPE'] in ['AS', 'ST'] and row['FoulOffBall'] == 0:
            if current_possession_team == 'HomeTeam':
                away_possessions += 1
                current_possession_team = 'AwayTeam'
            else:
                home_possessions += 1
                current_possession_team = 'HomeTeam'
        elif row['PLAYTYPE'] == 'EG':
            home_possessions == 0
        elif row['PLAYTYPE'] == 'EG':
            away_possessions == 0
        elif row['PLAYTYPE'] == 'BP' and row['CODETEAM'] == row['HomeTeam'] and row['PERIOD'] != 1:
            home_possessions += 1
            current_possession_team = 'HomeTeam'
        elif row['PLAYTYPE'] == 'BP' and row['CODETEAM'] == row['AwayTeam'] and row['PERIOD'] != 1:
            away_possessions += 1
            current_possession_team = 'AwayTeam'
        else:
            pass
        alldata.at[index, 'HomeTeamInPossession'] = home_possessions
        alldata.at[index, 'AwayTeamInPossession'] = away_possessions
    
    alldata['HomeTeamInPossession2'] = alldata['HomeTeamInPossession']
    alldata['AwayTeamInPossession2'] = alldata['AwayTeamInPossession']
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['PLAYTYPE'].isin(['2FGA', '3FGA', 'O','JB','OF','RV','BP'])) & (alldata['CODETEAM'] == alldata['AwayTeam'])
        & ((alldata['POTENTIALERROR'] == 0) | (alldata['POTENTIALERROR2'] == 1)) & (alldata['OFFnotTO'] == 0),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['PLAYTYPE'].isin(['2FGA', '3FGA', 'O','JB','OF','RV','BP'])) & (alldata['CODETEAM'] == alldata['HomeTeam'])
        & ((alldata['POTENTIALERROR'] == 0) | (alldata['POTENTIALERROR2'] == 1)) & (alldata['OFFnotTO'] == 0),'', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['FoulOffBall'] == 1) & (alldata['CODETEAM'] == alldata['HomeTeam'])& (alldata['And1Assisted'] == 0)
        & (alldata['POTENTIALERROR'] == 0),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['FoulOffBall'] == 1)  & (alldata['CODETEAM'] == alldata['AwayTeam']) & (alldata['And1Assisted'] == 0)
        & (alldata['POTENTIALERROR'] == 0),'', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['UnsportsBasket'] == 1) & (alldata['CODETEAM'] != alldata['HomeTeam'])
        & (alldata['POTENTIALERROR'] == 0),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['UnsportsBasket'] == 1)  & (alldata['CODETEAM'] != alldata['AwayTeam'])
        & (alldata['POTENTIALERROR'] == 0),'', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['AssistedBasket'] == 1) & (alldata['CODETEAM'] == alldata['AwayTeam'])
        & (alldata['POTENTIALERROR'] == 0),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['AssistedBasket'] == 1)  & (alldata['CODETEAM'] == alldata['HomeTeam'])
        & (alldata['POTENTIALERROR'] == 0),'', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['FirstFTAst'] == 1) & (alldata['CODETEAM'] == alldata['AwayTeam'])
        & (alldata['POTENTIALERROR'] == 0),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['FirstFTAst'] == 1)  & (alldata['CODETEAM'] == alldata['HomeTeam'])
        & (alldata['POTENTIALERROR'] == 0),'', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['And1Assisted'] == 1) & (alldata['CODETEAM'] == alldata['AwayTeam'])
        & (alldata['POTENTIALERROR'] == 0),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['And1Assisted'] == 1)  & (alldata['CODETEAM'] == alldata['HomeTeam'])
        & (alldata['POTENTIALERROR'] == 0),'', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['PLAYTYPE'].isin(['CM','FV','C','CMT','CMU','B'])) & (alldata['CODETEAM'] == alldata['HomeTeam']) &(alldata['FoulOffBall'] != 1)
        & (alldata['POTENTIALERROR'] == 0),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['PLAYTYPE'].isin(['CM','FV','C','CMT','CMU','B'])) & (alldata['CODETEAM'] == alldata['AwayTeam']) &(alldata['FoulOffBall'] != 1)
        & (alldata['POTENTIALERROR'] == 0),'', alldata['AwayTeamInPossession2'])
    
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['PLAYTYPE'].isin(['TO'])) & (alldata['CODETEAM'] == alldata['AwayTeam']) & (alldata['TOSteal'] == 1)
        & (alldata['POTENTIALERROR'] == 0),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['PLAYTYPE'].isin(['TO'])) & (alldata['CODETEAM'] == alldata['HomeTeam']) & (alldata['TOSteal'] == 1)
        & (alldata['POTENTIALERROR'] == 0),'', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        (alldata['PLAYTYPE'].isin(['2FGM', '3FGM'])) & (alldata['CODETEAM'] == alldata['AwayTeam']) & (alldata['And1'] == 1),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        (alldata['PLAYTYPE'].isin(['2FGM', '3FGM'])) & (alldata['CODETEAM'] == alldata['HomeTeam']) & (alldata['And1'] == 1),'', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        ((alldata['PLAYTYPE']).isin(['FTA','FTM'])) & (alldata['CODETEAM'] == alldata['AwayTeam']) & ( (alldata['MissedFTDreb'] == 1) | (alldata['MissedFTOreb'] == 1)),
        '', 
        alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        ((alldata['PLAYTYPE']).isin(['FTA','FTM'])) & (alldata['CODETEAM'] == alldata['HomeTeam']) & ( (alldata['MissedFTDreb'] == 1) | (alldata['MissedFTOreb'] == 1)),'', 
        alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where(
        ((alldata['PLAYTYPE']).isin(['FTA','FTM'])) & (alldata['CODETEAM'] == alldata['AwayTeam']) & ( (alldata['Last_FT'] != 1)
                                                                                                      ),'',  alldata['HomeTeamInPossession2'])
    alldata['AwayTeamInPossession2'] = np.where(
        ((alldata['PLAYTYPE']).isin(['FTA','FTM'])) & (alldata['CODETEAM'] == alldata['HomeTeam']) & ( (alldata['Last_FT'] != 1)
                                                                                                      ),'',  alldata['AwayTeamInPossession2'])
    alldata['HomeTeamInPossession2'] = np.where(
        ((alldata['PLAYTYPE']).isin(['D','ST'])) & (alldata['CODETEAM'] == alldata['HomeTeam']) & (alldata['LastPossessionOfQuarter'] == 1),'', alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where(
        ((alldata['PLAYTYPE']).isin(['D','ST'])) & (alldata['CODETEAM'] == alldata['AwayTeam']) & (alldata['LastPossessionOfQuarter'] == 1), '', alldata['AwayTeamInPossession2'])
    
    alldata['HomeTeamInPossession2'] = np.where( (alldata['LastPossessionOfQuarter'] == 1) &
        ~alldata['PLAYTYPE'].isin(['D','ST']) & (alldata['CODETEAM'] == alldata['AwayTeam']), '',  alldata['HomeTeamInPossession2'])
    
    alldata['AwayTeamInPossession2'] = np.where( (alldata['LastPossessionOfQuarter'] == 1) &
        ~alldata['PLAYTYPE'].isin(['D','ST']) & (alldata['CODETEAM'] == alldata['HomeTeam']),'', alldata['AwayTeamInPossession2'])
    
    alldata = alldata[~alldata['PLAYTYPE'].isin(['EG','EP'])]
    
    alldata['Phase'] = alldata['Phase_x']
    alldata['Round'] = alldata['Round_x']
    alldata['Team'] = alldata['CODETEAM']
    alldata['PlayerId'] = alldata['PLAYER_ID']
    alldata['PlayerName'] = alldata['PLAYER_x']
    alldata['Clock'] = alldata['MARKERTIME']
    alldata['Period'] = alldata['PERIOD']
    alldata['PlayType'] = alldata['PLAYTYPE']
    alldata['Action'] = alldata['ACTION']
    alldata['PointsScored'] = alldata['POINTS'].fillna(0)
    alldata['ShotCoord_X'] = alldata['COORD_X']
    alldata['ShotCoord_Y'] = alldata['COORD_Y']
    alldata['ShotZone'] = alldata['ZONE']
    alldata['FastBreak'] = alldata['FASTBREAK'].fillna(0)
    alldata['SecondChance'] = alldata['SECOND_CHANCE'].fillna(0)
    alldata['PointsOffTurnover'] = alldata['POINTS_OFF_TURNOVER'].fillna(0)
    alldata['HomePossession'] = alldata['HomeTeamInPossession2']
    alldata['AwayPossession'] = alldata['AwayTeamInPossession2']
    alldata['PlayInfo'] = alldata['PLAYINFO']
    alldata['POINTS_A'] = alldata.groupby((alldata['PLAYTYPE'] == 'BP').cumsum())['POINTS_A_x'].transform(lambda x: x.ffill().fillna(0))
    alldata['POINTS_B'] = alldata.groupby((alldata['PLAYTYPE'] == 'BP').cumsum())['POINTS_B_x'].transform(lambda x: x.ffill().fillna(0))
    alldata = alldata[(abs(alldata['POINTS_A'] - alldata['POINTS_B']) <= 25) | (alldata['Period'] < 4)]
    
    # Return Clean Play by Play Dataset
    return alldata[['Season','Phase','Round','Gamecode','HomeTeam','AwayTeam','Period','Clock','NumberOfPlay',
                    'Team','PlayerId','PlayerName','PlayType','Action','PlayInfo','PointsScored','ShotCoord_X',
                    'ShotCoord_Y','ShotZone','FastBreak','SecondChance','PointsOffTurnover','PeriodSecondsElapsed',
                    'HomePossession','AwayPossession','HomePlayersOnCourt','AwayPlayersOnCourt','FoulOffBall','And1','TOSteal',
                    'LastPossessionOfQuarter','And1Assisted','MissedFTOreb','POTENTIALERROR','POTENTIALERROR2','POTENTIALERROR3',
                    'UnsportsFT','techFT','UnsportsBasket','Last_FT']].sort_values(by=['Season','Gamecode','NumberOfPlay'],ascending=[True,True,True])


# In[5]:


cleaned_data = clean_playbyplay_data(playbyplay, boxscore, shotdata)


# In[6]:


cleaned_data.head()


# In[7]:


def individual_player_breakdown(cleaned_data, boxdata):

    '''
    
    Break play by play data into play specific datasets and aggregate events while each player is on the court
    Unique weighting system to determine players' impact on each possession 
        - (i.e player recieves more credit for offensive possession if they took the shot)
    Add in opponent offense/defense statistics for future calculations of elo ratings
    Add in how each possession began (used later to increase/decrease probabilities when determining transiation matrices)
    
    Returns exploded possession by possession dataset for each player, with outcomes and player impact for both offense and defense

    '''
    
    # Breakdown play by play for each player
    cleaned_data_longhome = cleaned_data.explode('HomePlayersOnCourt')
    cleaned_data_longaway = cleaned_data.explode('AwayPlayersOnCourt')
    
    cleaned_data_longhome2 = cleaned_data_longhome[(cleaned_data_longhome['Team'] == cleaned_data_longhome['HomeTeam'])]
    cleaned_data_longaway2 = cleaned_data_longaway[(cleaned_data_longaway['Team'] == cleaned_data_longaway['AwayTeam'])]
    
    cleaned_data_longhomeNew = cleaned_data.explode('HomePlayersOnCourt')
    cleaned_data_longawayNew = cleaned_data.explode('AwayPlayersOnCourt')
    
    playtypes_away = ["FTA", "FTM", "2FGM", "3FGM", "2FGA","3FGA","TO",'O','AS']
    playtypes_home = ["FV", "CM", "ST","D"]
    
    cleaned_data_longhome2New = cleaned_data_longhomeNew[
        (cleaned_data_longhomeNew['AwayPossession'] != "") &
        ( (cleaned_data_longhomeNew['PlayType'].isin(playtypes_away) & 
             (cleaned_data_longhomeNew['Team'] == cleaned_data_longhomeNew['AwayTeam'])) |
            (cleaned_data_longhomeNew['PlayType'].isin(playtypes_home) & 
             (cleaned_data_longhomeNew['Team'] == cleaned_data_longhomeNew['HomeTeam']))  )]
    
    cleaned_data_longaway2New = cleaned_data_longawayNew[
        (cleaned_data_longawayNew['HomePossession'] != "") &
        ( (cleaned_data_longawayNew['PlayType'].isin(playtypes_away) & 
             (cleaned_data_longawayNew['Team'] == cleaned_data_longawayNew['HomeTeam'])) |
            (cleaned_data_longawayNew['PlayType'].isin(playtypes_home) & 
             (cleaned_data_longawayNew['Team'] == cleaned_data_longawayNew['AwayTeam'])) )]
    
    euroReboundHome = cleaned_data_longhome[(cleaned_data_longhome['PlayType'].isin(['D','FV','CM'])) & (cleaned_data_longhome['Team'] == cleaned_data_longhome['AwayTeam'])]
    euroReboundAway = cleaned_data_longaway[(cleaned_data_longaway['PlayType'].isin(['D','FV','CM'])) & (cleaned_data_longaway['Team'] == cleaned_data_longaway['AwayTeam'])]
    
    # Aggregate events for each player both home/away and offense/defense
    homestats_for = cleaned_data_longhome2.groupby(['Season', 'Gamecode','Phase', 'HomePlayersOnCourt', 'HomePossession']).agg(
        fta_for_team= ('PlayType', lambda x: x.isin(['FTA', 'FTM']).sum()),
        ftm_for_team =('PlayType', lambda x: (x == 'FTM').sum()),
        to_for_team=('PlayType', lambda x: (x == 'TO').sum()),
        three_made_for_team=('PlayType', lambda x: (x == '3FGM').sum()),
        three_missed_for_team=('PlayType', lambda x: (x == '3FGA').sum()),
        two_made_for_team=('PlayType', lambda x: (x == '2FGM').sum()),
        two_missed_for_team=('PlayType', lambda x: (x == '2FGA').sum()),
        oreb_for_team=('PlayType', lambda x: (x == 'O').sum()),
        ast_for_team=('PlayType', lambda x: (x == 'AS').sum()),).reset_index()
    
    awaystats_for = cleaned_data_longaway2.groupby(['Season', 'Gamecode', 'Phase','AwayPlayersOnCourt', 'AwayPossession']).agg(
        fta_for_team=('PlayType', lambda x: x.isin(['FTA', 'FTM']).sum()),
        ftm_for_team=('PlayType', lambda x: (x == 'FTM').sum()),
        to_for_team=('PlayType', lambda x: (x == 'TO').sum()),
        three_made_for_team=('PlayType', lambda x: (x == '3FGM').sum()),
        three_missed_for_team=('PlayType', lambda x: (x == '3FGA').sum()),
        two_made_for_team=('PlayType', lambda x: (x == '2FGM').sum()),
        two_missed_for_team=('PlayType', lambda x: (x == '2FGA').sum()),
        oreb_for_team=('PlayType', lambda x: (x == 'O').sum()),
        ast_for_team=('PlayType', lambda x: (x == 'AS').sum()),).reset_index()
    
    homestats_against = cleaned_data_longhome2New.groupby(['Season', 'Gamecode', 'Phase', 'HomePlayersOnCourt', 'AwayPossession']).agg(
        fta_against_team=('PlayType', lambda x: x.isin(['FTA', 'FTM']).sum()),
        ftm_against_team=('PlayType', lambda x: (x == 'FTM').sum()),
        to_against_team=('PlayType', lambda x: (x == 'TO').sum()),
        three_made_against_team=('PlayType', lambda x: (x == '3FGM').sum()),
        three_missed_against_team=('PlayType', lambda x: (x == '3FGA').sum()),
        two_made_against_team=('PlayType', lambda x: (x == '2FGM').sum()),
        two_missed_against_team=('PlayType', lambda x: (x == '2FGA').sum()),
        oreb_against_team=('PlayType', lambda x: (x == 'O').sum()),
        ast_against_team=('PlayType', lambda x: (x == 'AS').sum()),
    ).reset_index()
    
    awaystats_against = cleaned_data_longaway2New.groupby(['Season', 'Gamecode', 'Phase','AwayPlayersOnCourt', 'HomePossession']).agg(
        fta_against_team=('PlayType', lambda x: x.isin(['FTA', 'FTM']).sum()),
        ftm_against_team=('PlayType', lambda x: (x == 'FTM').sum()),
        to_against_team=('PlayType', lambda x: (x == 'TO').sum()),
        three_made_against_team=('PlayType', lambda x: (x == '3FGM').sum()),
        three_missed_against_team=('PlayType', lambda x: (x == '3FGA').sum()),
        two_made_against_team=('PlayType', lambda x: (x == '2FGM').sum()),
        two_missed_against_team=('PlayType', lambda x: (x == '2FGA').sum()),
        oreb_against_team=('PlayType', lambda x: (x == 'O').sum()),
        ast_against_team=('PlayType', lambda x: (x == 'AS').sum()),
    ).reset_index()
    
    homedefstats = cleaned_data_longhome.groupby(['Season', 'Gamecode','Phase','HomeTeam' ,'HomePlayersOnCourt', 'AwayPossession']).agg(
        dreb_for_team=('PlayType', lambda x: (x == 'D').sum()),
        block_for_team=('PlayType', lambda x: (x == 'FV').sum()),
        foul_for_team=('PlayType', lambda x: (x == 'CM').sum()),
        steal_for_team=('PlayType', lambda x: (x == 'ST').sum()),).reset_index()
    
    awaydefstats = cleaned_data_longaway.groupby(['Season', 'Gamecode', 'Phase','AwayTeam','AwayPlayersOnCourt', 'HomePossession']).agg(
        dreb_for_team=('PlayType', lambda x: (x == 'D').sum()),
        block_for_team=('PlayType', lambda x: (x == 'FV').sum()),
        foul_for_team=('PlayType', lambda x: (x == 'CM').sum()),
        steal_for_team=('PlayType', lambda x: (x == 'ST').sum()),).reset_index()
    
    print("5")
    
    # Time of Possession
    home_timeofpossession = cleaned_data.groupby(['Season', 'Gamecode', 'HomePossession']).agg(
        min_seconds_elapsed_for=('PeriodSecondsElapsed', 'min'),
        max_seconds_elapsed_for=('PeriodSecondsElapsed', 'max')).reset_index()
    
    home_timeofpossession['Duration'] = home_timeofpossession['max_seconds_elapsed_for'] - home_timeofpossession['min_seconds_elapsed_for']
    
    away_timeofpossession = cleaned_data.groupby(['Season', 'Gamecode','AwayPossession']).agg(
        min_seconds_elapsed_for=('PeriodSecondsElapsed', 'min'),
        max_seconds_elapsed_for=('PeriodSecondsElapsed', 'max')).reset_index()
    
    away_timeofpossession['Duration'] = away_timeofpossession['max_seconds_elapsed_for'] - away_timeofpossession['min_seconds_elapsed_for']
    
    
    
    # Merge Home/Away and For/Against stats with time of possession numbers 
    homestatsAgainst = homestats_against.merge(home_timeofpossession,left_on=['Season','Gamecode','AwayPossession'],right_on=['Season','Gamecode','HomePossession'])
    awayStatsAgainst = awaystats_against.merge(away_timeofpossession,left_on=['Season','Gamecode','HomePossession'],right_on=['Season','Gamecode','AwayPossession'])
    
    homestatsAgainst.rename(columns={'HomePlayersOnCourt': 'PlayerID', 'AwayPossession': 'Possession'}, inplace=True)
    awayStatsAgainst.rename(columns={'AwayPlayersOnCourt': 'PlayerID', 'HomePossession': 'Possession'}, inplace=True)
    
    PlayerStatsPerPossession_Against = pd.concat([homestatsAgainst,awayStatsAgainst], ignore_index=True)
    
    PlayerStatsPerPossession_Against = PlayerStatsPerPossession_Against[PlayerStatsPerPossession_Against['Possession'] != ""]
    
    PlayerStatsPerPossession_Against['Possession'] = PlayerStatsPerPossession_Against['Possession'].astype(float)
    
    PlayerStatsPerPossession_Against.sort_values(by=['PlayerID','Season','Gamecode','Possession'], ascending=[False,True,True,True],inplace=True)
    
    homestatsFor = homestats_for.merge(home_timeofpossession,left_on=['Season','Gamecode','HomePossession'],right_on=['Season','Gamecode','HomePossession'])
    
    awayStatsFor = awaystats_for.merge(away_timeofpossession,left_on=['Season','Gamecode','AwayPossession'],right_on=['Season','Gamecode','AwayPossession'])
    
    homestatsFor.rename(columns={'HomePlayersOnCourt': 'PlayerID', 'HomePossession': 'Possession'}, inplace=True)
    awayStatsFor.rename(columns={'AwayPlayersOnCourt': 'PlayerID', 'AwayPossession': 'Possession'}, inplace=True)
    
    PlayerStatsPerPossession_For = pd.concat([homestatsFor,awayStatsFor], ignore_index=True)
    
    PlayerStatsPerPossession_For = PlayerStatsPerPossession_For[PlayerStatsPerPossession_For['Possession'] != ""]
    
    PlayerStatsPerPossession_For['Possession'] = PlayerStatsPerPossession_For['Possession'].astype(float)
    
    PlayerStatsPerPossession_For.sort_values(by=['PlayerID','Season','Gamecode','Possession'], ascending=[False,True,True,True],inplace=True)
    
    homedefstats.rename(columns={'HomePlayersOnCourt': 'PlayerID', 'AwayPossession': 'Possession'}, inplace=True)
    awaydefstats.rename(columns={'AwayPlayersOnCourt': 'PlayerID', 'HomePossession': 'Possession'}, inplace=True)
    
    defstats = pd.concat([homedefstats,awaydefstats])
    
    defstats = defstats[defstats['Possession'] != ""]
    
    defstats['Possession'] = defstats['Possession'].astype(float)
    
    PlayerStatsPerPossession_For.sort_values(by=['PlayerID','Season','Gamecode','Possession'],ascending = [True,False,False,False], inplace=True)
    
    PlayerStatsPerPossession_Against2 = PlayerStatsPerPossession_Against.merge(defstats,left_on=['Season','Gamecode','Possession','PlayerID'],
                                                                              right_on=['Season','Gamecode','Possession','PlayerID'],how='left')
    PlayerStatsPerPossession_Against2['dreb_for_team'] = PlayerStatsPerPossession_Against2['dreb_for_team'].fillna(0)
    PlayerStatsPerPossession_Against2['steal_for_team'] = PlayerStatsPerPossession_Against2['steal_for_team'].fillna(0)
    PlayerStatsPerPossession_Against2['block_for_team'] = PlayerStatsPerPossession_Against2['block_for_team'].fillna(0)
    PlayerStatsPerPossession_Against2['foul_for_team'] = PlayerStatsPerPossession_Against2['foul_for_team'].fillna(0)
    
    
    # Player team stats per possession
    PlayerStatsPerPossession_Against2['PlayerPossessionNumber'] = PlayerStatsPerPossession_Against2.groupby(['PlayerID']).cumcount() + 1
    PlayerStatsPerPossession_For['PlayerPossessionNumber'] = PlayerStatsPerPossession_For.groupby(['PlayerID']).cumcount() + 1
    
    
    # Back to orignal exploded dataset, find actual player stats on each possession to calculate usage amongst the team
    cleaned_data_longhome['FTAPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['FTA','FTM'])),1,0)
    cleaned_data_longhome['FTMPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['FTM'])),1,0)
    
    
    cleaned_data_longhome['OrebPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['O'])),1,0)
    
    cleaned_data_longhome['DrebPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['D'])),1,0)
    
    cleaned_data_longhome['TOPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['TO'])),1,0)
    
    cleaned_data_longhome['3FGPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['3FGM','3FGA'])),1,0)
    
    cleaned_data_longhome['3FGMPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['3FGM'])),1,0)
    
    cleaned_data_longhome['2FGPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['2FGM','2FGA'])),1,0)
    
    cleaned_data_longhome['2FGMPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['2FGM'])),1,0)
    
    cleaned_data_longhome['FoulPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['CM'])),1,0)
    
    cleaned_data_longhome['BlockPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['FV'])),1,0)
    
    cleaned_data_longhome['STPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['ST'])),1,0)
    
    cleaned_data_longhome['AstPlayer'] = np.where((cleaned_data_longhome['PlayerId'] == cleaned_data_longhome['HomePlayersOnCourt'])&
                                                    ((cleaned_data_longhome['PlayType']).isin(['AS'])),1,0)
    
    cleaned_data_longaway['FTAPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['FTA','FTM'])),1,0)
    cleaned_data_longaway['FTMPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['FTM'])),1,0)
    
    cleaned_data_longaway['OrebPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['O'])),1,0)
    
    cleaned_data_longaway['DrebPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['D'])),1,0)
    
    cleaned_data_longaway['TOPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['TO'])),1,0)
    
    cleaned_data_longaway['3FGPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['3FGM','3FGA'])),1,0)
    
    cleaned_data_longaway['3FGMPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['3FGM'])),1,0)
    
    cleaned_data_longaway['2FGPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['2FGM','2FGA'])),1,0)
    
    cleaned_data_longaway['2FGMPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['2FGM'])),1,0)
    
    cleaned_data_longaway['FoulPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['CM'])),1,0)
    
    cleaned_data_longaway['BlockPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['FV'])),1,0)
    
    cleaned_data_longaway['STPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['ST'])),1,0)
    
    cleaned_data_longaway['AstPlayer'] = np.where((cleaned_data_longaway['PlayerId'] == cleaned_data_longaway['AwayPlayersOnCourt'])&
                                                    ((cleaned_data_longaway['PlayType']).isin(['AS'])),1,0)
    
    # Aggregate individual player stats per possession both home/away and for/against
    homeusage_for = cleaned_data_longhome.groupby(['Season', 'Gamecode','Phase','HomeTeam', 'HomePlayersOnCourt', 'HomePossession']).agg(
        fta_player=('FTAPlayer', 'sum'),
        ftm_player=('FTMPlayer', 'sum'),
        to_player = ('TOPlayer', 'sum'),
        oreb_player=('OrebPlayer', 'sum'),
        threefga_player=('3FGPlayer', 'sum'),
        threefgm_player=('3FGMPlayer', 'sum'),
        twoefga_player=('2FGPlayer', 'sum'),
        twoefgm_player=('2FGMPlayer', 'sum'),
        assist_player=('AstPlayer', 'sum'),).reset_index()
    
    awayusage_for = cleaned_data_longaway.groupby(['Season', 'Gamecode', 'Phase','AwayTeam','AwayPlayersOnCourt', 'AwayPossession']).agg(
        fta_player=('FTAPlayer', 'sum'),
        ftm_player=('FTMPlayer', 'sum'),
        to_player = ('TOPlayer', 'sum'),
        oreb_player=('OrebPlayer', 'sum'),
        threefga_player=('3FGPlayer', 'sum'),
        threefgm_player=('3FGMPlayer', 'sum'),
        twoefga_player=('2FGPlayer', 'sum'),
        twoefgm_player=('2FGMPlayer', 'sum'),
        assist_player=('AstPlayer', 'sum'),).reset_index()
    
    homeusage_against = cleaned_data_longhome.groupby(['Season', 'Gamecode','Phase','HomeTeam' ,'HomePlayersOnCourt', 'AwayPossession']).agg(
        dreb_player = ('DrebPlayer', 'sum'),
        steal_player=('STPlayer', 'sum'),
        block_player=('BlockPlayer', 'sum'),
        foul_player=('FoulPlayer', 'sum'),).reset_index()
    
    awayusage_against = cleaned_data_longaway.groupby(['Season', 'Gamecode', 'Phase','AwayTeam','AwayPlayersOnCourt', 'HomePossession']).agg(
        dreb_player = ('DrebPlayer', 'sum'),
        steal_player=('STPlayer', 'sum'),
        block_player=('BlockPlayer', 'sum'),
        foul_player=('FoulPlayer', 'sum'),).reset_index()
    
    print("7")
    
    
    # Calculate player impact on each defensive possession
    homeusage_against = homeusage_against[homeusage_against['AwayPossession'] != ""]
    awayusage_against = awayusage_against[awayusage_against['HomePossession'] != ""]
    homeusage_against['AwayPossession'] = homeusage_against['AwayPossession'].astype(float)
    awayusage_against['HomePossession'] = awayusage_against['HomePossession'].astype(float)
    
    homeusage_against.rename(columns={'HomePlayersOnCourt': 'PlayerID', 'AwayPossession': 'OppPossession',
                                     'HomeTeam':'Team'}, inplace=True)
    awayusage_against.rename(columns={'AwayPlayersOnCourt': 'PlayerID', 'HomePossession': 'OppPossession',
                                     'AwayTeam':'Team'}, inplace=True)
    
    PlayerUsagePerPossession_Against = pd.concat([homeusage_against,awayusage_against], ignore_index=True)
    
    PlayerUsagePerPossession_Against['UsageFactor'] = (
        PlayerUsagePerPossession_Against['dreb_player'] * 0.5 +
        PlayerUsagePerPossession_Against['steal_player'] * 2 +
        PlayerUsagePerPossession_Against['block_player'] * 1.5 +
                 PlayerUsagePerPossession_Against['foul_player']+.4 + 0.2)
    
    
    # Calculate player impact on each offensive possession
    homeusage_for = homeusage_for[homeusage_for['HomePossession'] != ""]
    awayusage_for = awayusage_for[awayusage_for['AwayPossession'] != ""]
    homeusage_for['HomePossession'] = homeusage_for['HomePossession'].astype(float)
    awayusage_for['AwayPossession'] = awayusage_for['AwayPossession'].astype(float)
    
    homeusage_for.rename(columns={'HomePlayersOnCourt': 'PlayerID', 'HomePossession': 'Possession',
                                     'HomeTeam':'Team'}, inplace=True)
    awayusage_for.rename(columns={'AwayPlayersOnCourt': 'PlayerID', 'AwayPossession': 'Possession',
                                     'AwayTeam':'Team'}, inplace=True)
    
    PlayerUsagePerPossession_For = pd.concat([homeusage_for,awayusage_for], ignore_index=True)
    
    PlayerUsagePerPossession_For['UsageFactor'] = (
        PlayerUsagePerPossession_For['threefga_player'] * 1 +  
        PlayerUsagePerPossession_For['twoefga_player'] * 1 +   
        PlayerUsagePerPossession_For['fta_player'] * 0.44 +    
        PlayerUsagePerPossession_For['assist_player'] * 0.7 + 
        PlayerUsagePerPossession_For['to_player'] * 1 + 
        PlayerUsagePerPossession_For['oreb_player'] * .5 + .1 )
    
    
    # Calculate total usage of each team on each defensive possession so that we can find ratio of player to team
    teamsumagainst = PlayerUsagePerPossession_Against.groupby(by=['Season','Gamecode','Team','OppPossession'])['UsageFactor'].sum().reset_index()
    teamsumagainst = teamsumagainst.rename(columns={'UsageFactor': 'TeamUsage'})
    
    PlayerUsagePerPossession_Against2 = pd.merge(
        PlayerUsagePerPossession_Against,
        teamsumagainst,
        on=['Season', 'Gamecode', 'Team', 'OppPossession'],
        how='left')
    
    PlayerUsagePerPossession_Against2=PlayerUsagePerPossession_Against2.sort_values(by=['Season','Gamecode','OppPossession'])
    
    PlayerUsagePerPossession_Against2['UsagePercent'] = PlayerUsagePerPossession_Against2['UsageFactor']/PlayerUsagePerPossession_Against2['TeamUsage']
    
    # Calculate total usage of each team on each offensive possession so that we can find ratio of player to team
    teamsum = PlayerUsagePerPossession_For.groupby(by=['Season','Gamecode','Team','Possession'])['UsageFactor'].sum().reset_index()
    
    teamsum = teamsum.rename(columns={'UsageFactor': 'TeamUsage'})
    
    PlayerUsagePerPossession_For2 = pd.merge(
        PlayerUsagePerPossession_For,
        teamsum,
        on=['Season', 'Gamecode', 'Team', 'Possession'],
        how='left')
    
    PlayerUsagePerPossession_For2=PlayerUsagePerPossession_For2.sort_values(by=['Season','Gamecode','Possession'])
    
    PlayerUsagePerPossession_For2['UsagePercent'] = PlayerUsagePerPossession_For2['UsageFactor']/PlayerUsagePerPossession_For2['TeamUsage']
    
    
    # Join in playerIDs and then For/Against together, add in new aggregate columns
    playerids = boxdata[['Player_ID','Player','Team','Gamecode','Season']].drop_duplicates()
    playerids['Player_ID'] = playerids['Player_ID'].str.strip()
    
    PlayerStatsPerPossession_ForX = PlayerStatsPerPossession_For.merge(playerids,left_on=['PlayerID','Season','Gamecode'],right_on=['Player_ID','Season','Gamecode'],how='left')
    PlayerStatsPerPossession_AgainstX = PlayerStatsPerPossession_Against2.merge(playerids,left_on=['PlayerID','Season','Gamecode'],right_on=['Player_ID','Season','Gamecode'],how='left')
    
    OffensePlayerData = pd.merge(
        PlayerStatsPerPossession_ForX,
        PlayerUsagePerPossession_For2,
        on=['Season', 'Gamecode', 'Possession','PlayerID'],
        how='left')
    
    DefensePlayerData = pd.merge(
        PlayerStatsPerPossession_AgainstX,
        PlayerUsagePerPossession_Against2,
        left_on=['Season', 'Gamecode', 'Possession','PlayerID'],
        right_on=['Season','Gamecode','OppPossession','PlayerID'],
        how='left')
    
    OffensePlayerData['three_fga_for_team'] = OffensePlayerData['three_made_for_team'] + OffensePlayerData['three_missed_for_team']
    OffensePlayerData['two_fga_for_team'] = OffensePlayerData['two_made_for_team'] + OffensePlayerData['two_missed_for_team']
    DefensePlayerData['three_fga_against_team'] = DefensePlayerData['three_made_against_team'] + DefensePlayerData['three_missed_against_team']
    DefensePlayerData['two_fga_against_team'] = DefensePlayerData['two_made_against_team'] + DefensePlayerData['two_missed_against_team']
    
    OffensePlayerData = OffensePlayerData.sort_values(by=['Season','PlayerID','Gamecode','Possession'],ascending=[False,False,False,False])
    OffensePlayerData['PlayerPossessionNumber2'] = OffensePlayerData.groupby(['PlayerID']).cumcount() + 1
    
    OffensePlayerData['Phase'] = OffensePlayerData['Phase_x']
    OffensePlayerData['duration_for_team'] = OffensePlayerData['Duration']
    OffensePlayerData['Team'] = OffensePlayerData['Team_x']
    
    DefensePlayerData = DefensePlayerData.sort_values(by=['Season','PlayerID','Gamecode','Possession'],ascending=[False,False,False,False])
    DefensePlayerData['PlayerPossessionNumber2'] = DefensePlayerData.groupby(['PlayerID']).cumcount() + 1
    
    DefensePlayerData['Phase'] = DefensePlayerData['Phase_x']
    DefensePlayerData['duration_against_team'] = DefensePlayerData['Duration']
    DefensePlayerData['Team'] = DefensePlayerData['Team_x']
    
    
    # Find Team Offense Rolling averages for comparison to create Elo Ratings. If less than 5 games in the season, use the league averages
    OffenseTeamData = OffensePlayerData
    DefenseTeamData = DefensePlayerData
    
    OffenseTeamData['three_fga_for_team'] = OffenseTeamData['three_made_for_team'] + OffenseTeamData['three_missed_for_team']
    OffenseTeamData['two_fga_for_team'] = OffenseTeamData['two_made_for_team'] + OffenseTeamData['two_missed_for_team']
    
    OffenseTeamData2 = OffenseTeamData.groupby(by=['Season','Gamecode','Team_x'])[['fta_for_team','ftm_for_team',
                                                                                     'to_for_team','three_made_for_team','three_missed_for_team',
                                                                                     'three_fga_for_team', 'two_made_for_team','two_missed_for_team',
                                                                             'two_fga_for_team','oreb_for_team','ast_for_team','Duration']].mean().reset_index()
    
    OffenseTeamData2 = OffenseTeamData2.sort_values(by=['Season','Team_x','Gamecode'],ascending=[False,False,False])
    OffenseTeamData2['GameNumber'] = OffenseTeamData2.groupby(['Team_x','Season']).cumcount() + 1
    
    
    league_avg = OffenseTeamData2[OffenseTeamData2['Season'] == OffenseTeamData2['Season'].max()][['fta_for_team', 'ftm_for_team', 'to_for_team',
                                                                                                  'three_made_for_team',	'three_missed_for_team',
                                                                                                   'three_fga_for_team',	'two_made_for_team'	,
                                                                                                   'two_missed_for_team',	'two_fga_for_team'	,
                                                                                                   'oreb_for_team',	'ast_for_team'	,'Duration',]].mean()
    def rolling_with_league_avg(group, stat, league_avg):
        rolling_avg = group[stat].rolling(window=10, min_periods=1).mean()
        rolling_avg = rolling_avg.where(group['GameNumber'] > 7, other=league_avg[stat])
        return rolling_avg
    
    OffenseTeamData2['fta_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'fta_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['ftm_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'ftm_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['to_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'to_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['three_made_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'three_made_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['three_missed_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'three_missed_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['three_fga_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'three_fga_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['two_made_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'two_made_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['two_missed_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'two_missed_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['two_fga_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'two_fga_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['oreb_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'oreb_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['ast_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'ast_for_team', league_avg)).reset_index(level=0, drop=True)
    OffenseTeamData2['duration_RollingAvg'] = OffenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg(x, 'Duration', league_avg)).reset_index(level=0, drop=True)
    
    # Add in Opposing Team name to join in defense rolling averages
    firstteam = boxdata.groupby(by=['Season','Gamecode'])['Team'].max().reset_index()
    secondteam = boxdata.groupby(by=['Season','Gamecode'])['Team'].min().reset_index()
    
    bothteams = firstteam.merge(secondteam,left_on=['Season','Gamecode'],right_on=['Season','Gamecode'],how='left')
    bothteams['Team1'] = bothteams['Team_x']
    bothteams['Team2'] = bothteams['Team_y']
    bothteams['SeasonNEW'] = bothteams['Season']
    bothteams['GamecodeNEW'] = bothteams['Gamecode']
    bothteams.drop(columns=['Team_x','Team_y','Season','Gamecode'],inplace=True)
    
    OffenseTeamData3 = OffenseTeamData2.merge(bothteams, left_on=['Season', 'Gamecode'], right_on=['SeasonNEW', 'GamecodeNEW'], how='left')
    
    OffenseTeamData3['OpposingTeam'] = np.where(OffenseTeamData3['Team1'] == OffenseTeamData3['Team_x'], OffenseTeamData3['Team2'], OffenseTeamData3['Team1'])
    
    OffenseTeamData3 = OffenseTeamData3[['Season','Gamecode','Team_x','OpposingTeam',
                                         'fta_RollingAvg','ftm_RollingAvg','to_RollingAvg','three_made_RollingAvg',
                                        'three_missed_RollingAvg','three_fga_RollingAvg','two_made_RollingAvg','two_missed_RollingAvg',
                                        'two_fga_RollingAvg','oreb_RollingAvg','ast_RollingAvg','duration_RollingAvg']]
    
    
    
    # Find Team Defense Rolling averages for comparison to create Elo Ratings. If less than 5 games in the season, use the league averages
    DefenseTeamData['three_fga_against_team'] = DefenseTeamData['three_made_against_team'] + DefenseTeamData['three_missed_against_team']
    DefenseTeamData['two_fga_against_team'] = DefenseTeamData['two_made_against_team'] + DefenseTeamData['two_missed_against_team']
    
    DefenseTeamData2 = DefenseTeamData.groupby(by=['Season','Gamecode','Team_x'])[['fta_against_team','ftm_against_team',
                                                                                     'to_against_team','three_made_against_team','three_missed_against_team',
                                                                                     'three_fga_against_team', 'two_made_against_team','two_missed_against_team',
                                                                             'two_fga_against_team','oreb_against_team','ast_against_team','Duration',
                                                                                  'dreb_for_team','block_for_team','steal_for_team','foul_for_team']].mean().reset_index()
    
    DefenseTeamData2 = DefenseTeamData2.sort_values(by=['Season','Team_x','Gamecode'],ascending=[False,False,False])
    DefenseTeamData2['GameNumber'] = DefenseTeamData2.groupby(['Team_x', 'Season']).cumcount() + 1
    
    league_avg2 = DefenseTeamData2[DefenseTeamData2['Season'] == DefenseTeamData2['Season'].max()][['fta_against_team', 'ftm_against_team', 'to_against_team',
                                                                                                  'three_made_against_team',	'three_missed_against_team',
                                                                                                   'three_fga_against_team',	'two_made_against_team'	,
                                                                                                   'two_missed_against_team',	'two_fga_against_team'	,
                                                                                                   'oreb_against_team',	'ast_against_team'	,'Duration',
                                                                                                   'dreb_for_team','block_for_team','steal_for_team','foul_for_team']].mean()
    def rolling_with_league_avg2(group, stat, league_avg2):
        rolling_avg = group[stat].rolling(window=10, min_periods=1).mean()
        rolling_avg = rolling_avg.where(group['GameNumber'] > 7, other=league_avg2[stat])
        return rolling_avg
    
    DefenseTeamData2['fta_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'fta_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['ftm_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'ftm_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['to_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'to_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['three_made_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'three_made_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['three_missed_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'three_missed_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['three_fga_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'three_fga_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['two_made_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'two_made_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['two_missed_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'two_missed_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['two_fga_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'two_fga_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['oreb_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'oreb_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['ast_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'ast_against_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['duration_RollingAvg'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'Duration', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['dreb_RollingAvg_NONOPPTEAM'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'dreb_for_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['block_RollingAvg_NONOPPTEAM'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'block_for_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['steal_RollingAvg_NONOPPTEAM'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'steal_for_team', league_avg2)).reset_index(level=0, drop=True)
    DefenseTeamData2['foul_RollingAvg_NONOPPTEAM'] = DefenseTeamData2.groupby('Team_x').apply(lambda x: rolling_with_league_avg2(x, 'foul_for_team', league_avg2)).reset_index(level=0, drop=True)
    
    print("11")
    
    # Add in Opposing Team name to join in offense rolling averages
    firstteam = boxdata.groupby(by=['Season','Gamecode'])['Team'].max().reset_index()
    secondteam = boxdata.groupby(by=['Season','Gamecode'])['Team'].min().reset_index()
    
    bothteams = firstteam.merge(secondteam,left_on=['Season','Gamecode'],right_on=['Season','Gamecode'],how='left')
    bothteams['Team1'] = bothteams['Team_x']
    bothteams['Team2'] = bothteams['Team_y']
    bothteams['SeasonNEW'] = bothteams['Season']
    bothteams['GamecodeNEW'] = bothteams['Gamecode']
    bothteams.drop(columns=['Team_x','Team_y','Season','Gamecode'],inplace=True)
    
    DefenseTeamData3 = DefenseTeamData2.merge(bothteams, left_on=['Season', 'Gamecode'], right_on=['SeasonNEW', 'GamecodeNEW'], how='left')
    
    DefenseTeamData3['OpposingTeam'] = np.where(DefenseTeamData3['Team1'] == DefenseTeamData3['Team_x'], DefenseTeamData3['Team2'], DefenseTeamData3['Team1'])
    
    DefenseTeamData3 = DefenseTeamData3[['Season','Gamecode','Team_x','OpposingTeam','dreb_RollingAvg_NONOPPTEAM','block_RollingAvg_NONOPPTEAM'
                      ,'steal_RollingAvg_NONOPPTEAM','foul_RollingAvg_NONOPPTEAM',
                                         'fta_RollingAvg','ftm_RollingAvg','to_RollingAvg','three_made_RollingAvg',
                                        'three_missed_RollingAvg','three_fga_RollingAvg','two_made_RollingAvg','two_missed_RollingAvg',
                                        'two_fga_RollingAvg','oreb_RollingAvg','ast_RollingAvg','duration_RollingAvg']]
    
    DefenseTeamData3.rename(columns={'Team_x': 'Team'}, inplace=True)
    
    # Add in how each possession was started. 4 options: After a Score, After a deadlball, after turnover in play, or after defensive rebound
    homeaway = cleaned_data[['Season','Gamecode','HomeTeam','AwayTeam']].drop_duplicates()
    OffensePlayerData2 = OffensePlayerData.merge(homeaway, left_on=['Season','Gamecode'], right_on=['Season','Gamecode'],how='left')
    DefensePlayerData2 = DefensePlayerData.merge(homeaway, left_on=['Season','Gamecode'], right_on=['Season','Gamecode'],how='left')
    OffensePlayerData2['Home'] = np.where(OffensePlayerData2['HomeTeam'] == OffensePlayerData2['Team'],1,0)
    DefensePlayerData2['Home'] = np.where(DefensePlayerData2['HomeTeam_y'] == DefensePlayerData2['Team'],1,0)
    
    rp = cleaned_data.groupby(['Season', 'Gamecode', 'HomeTeam','HomePossession']).apply(lambda x: x.iloc[0][['PlayType']]).reset_index()
    rp.rename(columns={'HomePossession': 'Possession',
                      'HomeTeam':'Team'}, inplace=True)
    rp2 = cleaned_data.groupby(['Season', 'Gamecode','AwayTeam', 'AwayPossession']).apply(lambda x: x.iloc[0][['PlayType']]).reset_index()
    rp2.rename(columns={'AwayPossession': 'Possession',
                      'AwayTeam':'Team'}, inplace=True)
    resultpossessions = pd.concat([rp,rp2])
    resultpossessions['Possession'] = np.where(resultpossessions['Possession'] == "",10000,resultpossessions['Possession'])
    resultpossessions['Possession'] = resultpossessions['Possession'].astype(float)
    resultpossessions['SOP_AfterPoints'] = np.where(resultpossessions['PlayType'].isin(['2FGM','3FGM','AS','FTM']), 1, 0)
    resultpossessions['SOP_DeadBall'] = np.where(resultpossessions['PlayType'].isin(['TO','CM','BP','OF']), 1, 0)
    resultpossessions['SOP_AfterTurnover'] = np.where(resultpossessions['PlayType'].isin(['ST']), 1, 0)
    resultpossessions['SOP_DefensiveRebound'] = np.where(resultpossessions['PlayType'].isin(['D','2FGA','3FGA','FTA','FV']), 1, 0)
    OffensePlayerData2['OpposingTeam'] = np.where(OffensePlayerData2['Team'] == OffensePlayerData2['HomeTeam'],OffensePlayerData2['AwayTeam'],OffensePlayerData2['HomeTeam'])
    
    
    # Final Offense Player Dataset with Team Rolling Averages for Comparison and Start of Possession Data
    OffensePlayerDataNEW = OffensePlayerData2.merge(resultpossessions, left_on=['Season','Gamecode','Team','Possession'], 
                           right_on=['Season','Gamecode','Team','Possession'],how='left')
    
    
    DefensePlayerData1 = DefensePlayerData2.merge(bothteams,left_on=['Season','Gamecode'],right_on=['SeasonNEW','GamecodeNEW'],how='left')
    DefensePlayerData1['OpposingTeam'] = np.where(DefensePlayerData1['Team'] == DefensePlayerData1['HomeTeam_y'],DefensePlayerData1['AwayTeam_y'],DefensePlayerData1['HomeTeam_y'])
    resultpossessions['JoinTeamD'] = resultpossessions['Team']
    resultpossessions = resultpossessions.drop(columns='Team')
    
    
    # Final Defense Player Dataset with Team Rolling Averages for Comparison and Start of Possession Data
    DefensePlayerDataNEW = DefensePlayerData1.merge(resultpossessions, left_on=['Season','Gamecode','OpposingTeam','OppPossession'],
                            right_on=['Season','Gamecode','JoinTeamD','Possession'],how='left')
    
    
    # Add in Usage Rolling averages
    DefenseTeamData34 = DefenseTeamData3.rename(columns={'Team': 'Team1'})
    OffensePlayerDataNEW1 = OffensePlayerDataNEW.merge(DefenseTeamData34, left_on=['Season','Gamecode','Team_x'], right_on=['Season','Gamecode','OpposingTeam'],how='left')
    OffenseTeamData34 = OffenseTeamData3.rename(columns={'Team': 'Team1'})
    DefensePlayerDataNEW1 = DefensePlayerDataNEW.merge(OffenseTeamData34, left_on=['Season','Gamecode','Team_x'], right_on=['Season','Gamecode','OpposingTeam'],how='left')
    OffensePlayerDataNEW1['Usage_RollingAvg'] = .2
    DefensePlayerDataNEW1['Usage_RollingAvg'] = .2

    return OffensePlayerDataNEW1, DefensePlayerDataNEW1, homeusage_for, awayusage_for, homeusage_against, awayusage_against


# In[8]:


OffensePlayerDataNEW1, DefensePlayerDataNEW1, homeusage_for, awayusage_for, homeusage_against, awayusage_against  = individual_player_breakdown(cleaned_data,boxscore)


# In[9]:


OffensePlayerDataNEW1.head()


# In[10]:


def calculate_player_elo_ratings (OffensePlayerDataNEW1,DefensePlayerDataNEW1):

    """
    Calculates player level elo ratings using previously created player possession data.

    Returns player impact ratings for offense/defense eFG%, OReb/DReb, TO, and FTA Rate, as well as pace.
    
    """
    
    # default for k value
    n = 1.5
    
    # k values for each specific stat. the larger the k value, the mroe discrepency there is between very good and very bad at each stat
    k_values = {
        'two_made_for_team': .5,
        'two_missed_for_team': .5,
        'two_fga_for_team': .7,
        'three_made_for_team': .25,
        'three_missed_for_team': .25,
        'three_fga_for_team': .6,
        'fta_for_team': .6,
        'ftm_for_team': .4,
        'oreb_for_team': .65,        
        'to_for_team': .6,
        'Duration': .5,
        'UsagePercent': .5,
        'two_made_against_team': .5,
        'two_missed_against_team': .5,
        'two_fga_against_team': .5,
        'three_made_against_team': .25,
        'three_missed_against_team': .25,
        'three_fga_against_team': .4,
        'fta_against_team': .6,
        'ftm_against_team': .001,
        'oreb_against_team': .65,  
        'to_against_team': .6,}
    
    def elo_adjustment(current_elo, outcome, k):
        return current_elo + k * outcome
    
    initial_elo = 1500
    offense_stats_to_evaluate = [
        ('two_made_for_team', 'two_made_RollingAvg'),
        ('two_missed_for_team', 'two_missed_RollingAvg'),
        ('two_fga_for_team', 'two_fga_RollingAvg'),
        ('three_made_for_team', 'three_made_RollingAvg'),
        ('three_missed_for_team', 'three_missed_RollingAvg'),
        ('three_fga_for_team', 'three_fga_RollingAvg'),
        ('fta_for_team', 'fta_RollingAvg'),
        ('ftm_for_team', 'ftm_RollingAvg'),
        ('oreb_for_team', 'oreb_RollingAvg'),
        ('to_for_team', 'to_RollingAvg'),
        ('Duration', 'duration_RollingAvg'),
        ('UsagePercent', 'Usage_RollingAvg')]
    
    defense_stats_to_evaluate = [
        ('two_made_against_team', 'two_made_RollingAvg'),
        ('two_missed_against_team', 'two_missed_RollingAvg'),
        ('two_fga_against_team', 'two_fga_RollingAvg'),
        ('three_made_against_team', 'three_made_RollingAvg'),
        ('three_missed_against_team', 'three_missed_RollingAvg'),
        ('three_fga_against_team', 'three_fga_RollingAvg'),
        ('fta_against_team', 'fta_RollingAvg'),
        ('ftm_against_team', 'ftm_RollingAvg'),
        ('oreb_against_team', 'oreb_RollingAvg'),
        ('to_against_team', 'to_RollingAvg'),
        ('Duration', 'duration_RollingAvg'),
        ('UsagePercent', 'Usage_RollingAvg')]
    
    elo_offense_ratings_dict = {player_id: {stat[0]: initial_elo for stat in offense_stats_to_evaluate}
                                for player_id in OffensePlayerDataNEW1['PlayerID'].unique()}
    
    elo_defense_ratings_dict = {player_id: {stat[0]: initial_elo for stat in defense_stats_to_evaluate}
                                for player_id in DefensePlayerDataNEW1['PlayerID'].unique()}
    
    
    
    # Elo ratings for offense
    for _, row in OffensePlayerDataNEW1.iterrows():
        player_id = row['PlayerID']
        usage = row['UsagePercent']
        
        for stat, rolling_stat in offense_stats_to_evaluate:
            k = k_values.get(stat, .5)  
    
            if "Usage" not in stat:
                player_stat = row[stat] * usage
                rolling_stat_value = row[rolling_stat] * usage
            else:
                player_stat = row[stat]
                rolling_stat_value = row[rolling_stat]
    
            outcome = (player_stat - rolling_stat_value) / rolling_stat_value if rolling_stat_value else 0
    
            elo_offense_ratings_dict[player_id][stat] = elo_adjustment(elo_offense_ratings_dict[player_id][stat], outcome, k)
    
    # Elo ratings for defense 
    for _, row in DefensePlayerDataNEW1.iterrows():
        player_id = row['PlayerID']
        usage = row['UsagePercent']
        
        for stat, rolling_stat in defense_stats_to_evaluate:
            # Get the corresponding k value for the stat
            k = k_values.get(stat, 1)  # Default k value is 5 if not specified in the dictionary
    
            if "Usage" not in stat:
                player_stat = row[stat] * usage
                rolling_stat_value = row[rolling_stat] * usage
            else:
                player_stat = row[stat]
                rolling_stat_value = row[rolling_stat]
            
            # Calculate the outcome using the rolling stat value
            outcome = (player_stat - rolling_stat_value) / rolling_stat_value if rolling_stat_value else 0
            
            # Update the elo defense rating for the player
            elo_defense_ratings_dict[player_id][stat] = elo_adjustment(elo_defense_ratings_dict[player_id][stat], outcome, k)
    
    # Elo ratings into DataFrames and join for final ratings
    elo_offense_results = []
    for player_id, ratings in elo_offense_ratings_dict.items():
        result_row = {'PlayerID': player_id}
        result_row.update(ratings)
        elo_offense_results.append(result_row)
    
    elo_defense_results = []
    for player_id, ratings in elo_defense_ratings_dict.items():
        result_row = {'PlayerID': player_id}
        result_row.update(ratings)
        elo_defense_results.append(result_row)
    
    elo_offense_df = pd.DataFrame(elo_offense_results)
    elo_defense_df = pd.DataFrame(elo_defense_results)
    
    elo_offense_df.columns = [col + '_offense' if col != 'PlayerID' else col for col in elo_offense_df.columns]
    elo_defense_df.columns = [col + '_defense' if col != 'PlayerID' else col for col in elo_defense_df.columns]
    
    elo_combined_df = pd.merge(elo_offense_df, elo_defense_df, on='PlayerID')
    
    elo_combined_df = elo_combined_df.merge(OffensePlayerDataNEW1[['PlayerID', 'Player']].drop_duplicates(), 
                                            left_on='PlayerID', right_on='PlayerID', how='left')
    
    # Elo Ratings final dataset
    elo_combined_df.rename(columns={'two_made_for_team_offense': 'two_made_O',
                                    'two_missed_for_team_offense': 'two_miss_O',
                                    'two_fga_for_team_offense': 'two_attempt_O',
                                    'three_made_for_team_offense': 'three_made_O',
                                    'three_missed_for_team_offense': 'three_miss_O',
                                    'three_fga_for_team_offense': 'three_attempt_O',
                                    'fta_for_team_offense': 'fta_O',
                                    'ftm_for_team_offense': 'ftm_O',
                                    'oreb_for_team_offense': 'oreb_O',
                                    'to_for_team_offense': 'to_O',
                                    'Duration_offense': 'pace_O',
                                    'UsagePercent_offense': 'usage_O',
                                    'two_made_against_team_defense': 'two_made_D',
                                    'two_missed_against_team_defense': 'two_miss_D',
                                    'two_fga_against_team_defense': 'two_attempt_D',
                                    'three_made_against_team_defense': 'three_made_D',
                                    'three_missed_against_team_defense': 'three_miss_D',
                                    'three_fga_against_team_defense': 'three_attempt_D',
                                    'fta_against_team_defense': 'fta_D',
                                    'ftm_against_team_defense': 'ftm_D',
                                    'oreb_against_team_defense': 'oreb_D',
                                    'to_against_team_defense': 'to_D',
                                    'Duration_defense': 'pace_D',
                                    'UsagePercent_defense': 'usage_D'}, inplace=True)
    
    return elo_combined_df


# In[11]:


elo_combined_df = calculate_player_elo_ratings (OffensePlayerDataNEW1,DefensePlayerDataNEW1)


# In[12]:


elo_combined_df.head()


# In[13]:


def home_court_advantage(OffensePlayerDataNEW1, DefensePlayerDataNEW1):

    """
    Calculates home court advantage:
        - Compilies cumulative team outcomes when teams are playing at home vs playing away on both offense and defense.
        - Uses the outcomes to create a transition matrix for the home teams, away teams, and combined.
            - Assess the impact of all major stat categories (i.e shooting percentages, offensive rebounding, fouls, etc)

    Returns 4 transition matrices which are the percentage differences at each element of the transition matrix
        - Impact of home offense/defense , away offense/defense.
        - To be used alongside of team transition matrices used later.
    
    """
    
    # Home Court Advantage. group datasets by Home, Away and Nuetral, then create a transtion matrix for each to find the differences
    HomeOTeam = OffensePlayerDataNEW1[(OffensePlayerDataNEW1['Home'] == 1) & (OffensePlayerDataNEW1['Phase_x'] == 'RS')
    ].groupby(by=['Season', 'Gamecode', 'Team', 'Possession'])[
        ['fta_for_team', 'ftm_for_team', 'to_for_team', 'three_made_for_team', 'three_missed_for_team', 
         'two_made_for_team', 'two_missed_for_team', 'two_fga_for_team', 'three_fga_for_team', 
         'oreb_for_team', 'ast_for_team']].mean().reset_index()
    
    OTeam = OffensePlayerDataNEW1[OffensePlayerDataNEW1['Home'].isin([0, 1]) & (OffensePlayerDataNEW1['Phase_x'] == 'RS')
    ].groupby(by=['Team', 'Season', 'Gamecode', 'Possession'])[
        ['fta_for_team', 'ftm_for_team', 'to_for_team', 'three_made_for_team', 'three_missed_for_team', 
         'two_made_for_team', 'two_missed_for_team', 'two_fga_for_team', 'three_fga_for_team', 
         'oreb_for_team', 'ast_for_team']].mean().reset_index()
    
    AwayOTeam = OffensePlayerDataNEW1[(OffensePlayerDataNEW1['Home'] == 0) & (OffensePlayerDataNEW1['Phase_x'] == 'RS')
    ].groupby(by=['Season', 'Gamecode', 'Team', 'Possession'])[
        ['fta_for_team', 'ftm_for_team', 'to_for_team', 'three_made_for_team', 'three_missed_for_team', 
         'two_made_for_team', 'two_missed_for_team', 'two_fga_for_team', 'three_fga_for_team', 
         'oreb_for_team', 'ast_for_team']].mean().reset_index()
    
    DTeam = DefensePlayerDataNEW1[DefensePlayerDataNEW1['Home'].isin([0, 1]) & (DefensePlayerDataNEW1['Phase_x'] == 'RS')
    ].groupby(by=['Team', 'Season', 'Gamecode', 'OppPossession'])[
        ['fta_against_team', 'ftm_against_team', 'to_against_team', 'three_made_against_team', 
         'three_missed_against_team', 'two_made_against_team', 'two_missed_against_team', 
         'two_fga_against_team', 'three_fga_against_team', 'oreb_against_team', 'ast_against_team']].mean().reset_index()
    
    AwayDTeam = DefensePlayerDataNEW1[(DefensePlayerDataNEW1['Home'] == 0) & (DefensePlayerDataNEW1['Phase_x'] == 'RS')
    ].groupby(by=['Team', 'Season', 'Gamecode', 'OppPossession'])[
        ['fta_against_team', 'ftm_against_team', 'to_against_team', 'three_made_against_team', 
         'three_missed_against_team', 'two_made_against_team', 'two_missed_against_team', 
         'two_fga_against_team', 'three_fga_against_team', 'oreb_against_team', 'ast_against_team']].mean().reset_index()
    
    HomeDTeam = DefensePlayerDataNEW1[(DefensePlayerDataNEW1['Home'] == 1) & (DefensePlayerDataNEW1['Phase_x'] == 'RS')
    ].groupby(by=['Team', 'Season', 'Gamecode', 'OppPossession'])[
        ['fta_against_team', 'ftm_against_team', 'to_against_team', 'three_made_against_team', 
         'three_missed_against_team', 'two_made_against_team', 'two_missed_against_team', 
         'two_fga_against_team', 'three_fga_against_team', 'oreb_against_team', 'ast_against_team']].mean().reset_index()

    # Calcuates Transition Matrix for team offense
    def calculate_transition_matrix_team_offense(team_data, possessions_to_sim):
    
        team_data['TripToFTline_outcome'] = team_data['fta_for_team']
        team_data['ThreePointAttempt_outcome'] = team_data['three_fga_for_team']
        team_data['TwoPointAttempt_outcome'] = team_data['two_fga_for_team']
        team_data['Turnover_outcome'] = team_data['to_for_team']
        team_data['ThreePointMiss'] = team_data['three_missed_for_team']
        team_data['ThreePointMake'] = team_data['three_made_for_team']
        team_data['TwoPointMiss'] = team_data['two_missed_for_team']
        team_data['TwoPointMake'] = team_data['two_made_for_team']
        team_data['FTMiss'] = team_data['fta_for_team'] - team_data['ftm_for_team']
        team_data['FTMake'] = team_data['ftm_for_team']
    
        team_data['2ptOreb'] = np.where((team_data['oreb_for_team'] > 0) & (team_data['two_missed_for_team'] > 0), 
                                        np.minimum(team_data['oreb_for_team'], team_data['two_missed_for_team']), 0)
        team_data['2ptNotOreb'] = np.where((team_data['oreb_for_team'] == 0) & (team_data['two_missed_for_team'] > 0), 
                                           team_data['two_missed_for_team'], 0)
        team_data['3ptOreb'] = np.where((team_data['oreb_for_team'] > 0) & (team_data['three_missed_for_team'] > 0), 
                                        np.minimum(team_data['oreb_for_team'], team_data['three_missed_for_team']), 0)
        team_data['3ptNotOreb'] = np.where((team_data['oreb_for_team'] == 0) & (team_data['three_missed_for_team'] > 0), 
                                           team_data['three_missed_for_team'], 0)
    
        ft_missed = team_data['fta_for_team'] - team_data['ftm_for_team']
        team_data['FTOreb'] = np.where((team_data['oreb_for_team'] > 0) & (ft_missed > 0), 1, 0)
        team_data['FTNotOreb'] = 1 - team_data['FTOreb']
    
        states = ['Initial Possession', '3pt Attempt', '3pt Make', '3pt Miss', '2pt Attempt', '2pt Make', '2pt Miss', 
                  'Trip to FT Line', 'FT Attempt 1', 'FT Attempt 2', 'FT Make 1', 'FT Miss 1', 'FT Make 2', 'FT Miss 2', 'Turnover',
                  '2pt Oreb', '3pt Oreb', 'FT Oreb', '2pt NonOreb', '3pt NonOreb', 'FT NonOreb']
    
        transition_matrix = pd.DataFrame(0, index=states, columns=states)
    
        transition_matrix.loc['Initial Possession', 'Trip to FT Line'] = team_data['TripToFTline_outcome'].sum()
        transition_matrix.loc['Initial Possession', '3pt Attempt'] = team_data['ThreePointAttempt_outcome'].sum()
        transition_matrix.loc['Initial Possession', '2pt Attempt'] = team_data['TwoPointAttempt_outcome'].sum()
        transition_matrix.loc['Initial Possession', 'Turnover'] = team_data['Turnover_outcome'].sum()
    
        transition_matrix.loc['2pt Attempt', '2pt Make'] = team_data['TwoPointMake'].sum()
        transition_matrix.loc['2pt Attempt', '2pt Miss'] = team_data['TwoPointMiss'].sum()
    
        transition_matrix.loc['3pt Attempt', '3pt Make'] = team_data['ThreePointMake'].sum()
        transition_matrix.loc['3pt Attempt', '3pt Miss'] = team_data['ThreePointMiss'].sum()
    
        transition_matrix.loc['2pt Miss', '2pt Oreb'] = team_data['2ptOreb'].sum()
        transition_matrix.loc['2pt Miss', '2pt NonOreb'] = team_data['2ptNotOreb'].sum()
    
        transition_matrix.loc['3pt Miss', '3pt Oreb'] = team_data['3ptOreb'].sum()
        transition_matrix.loc['3pt Miss', '3pt NonOreb'] = team_data['3ptNotOreb'].sum()
    
        transition_matrix.loc['Trip to FT Line', 'FT Attempt 1'] = team_data['TripToFTline_outcome'].sum()
        transition_matrix.loc['FT Attempt 1', 'FT Make 1'] = team_data['FTMake'].sum()
        transition_matrix.loc['FT Attempt 1', 'FT Miss 1'] = team_data['FTMiss'].sum()
        transition_matrix.loc['FT Make 1', 'FT Attempt 2'] = team_data['FTMake'].sum()
        transition_matrix.loc['FT Miss 1', 'FT Attempt 2'] = team_data['FTMiss'].sum()
        transition_matrix.loc['FT Attempt 2', 'FT Make 2'] = team_data['FTMake'].sum()
        transition_matrix.loc['FT Attempt 2', 'FT Miss 2'] = team_data['FTMiss'].sum()
    
        transition_matrix.loc['FT Miss 2', 'FT Oreb'] = team_data['FTOreb'].sum()
        transition_matrix.loc['FT Miss 2', 'FT NonOreb'] = team_data['FTNotOreb'].sum()
    
        transition_matrix.loc['2pt Oreb', 'Initial Possession'] = team_data['2ptOreb'].sum()
        transition_matrix.loc['3pt Oreb', 'Initial Possession'] = team_data['3ptOreb'].sum()
        transition_matrix.loc['FT Oreb', 'Initial Possession'] = team_data['FTOreb'].sum()
    
        transition_matrix = transition_matrix.fillna(0)
    
        return transition_matrix
    
    def calculate_transition_matrix_team_defense(team_data, possessions_to_sim):
        team_data['TripToFTline_outcome'] = team_data['fta_against_team']
        team_data['ThreePointAttempt_outcome'] = team_data['three_fga_against_team']
        team_data['TwoPointAttempt_outcome'] = team_data['two_fga_against_team']
        team_data['Turnover_outcome'] = team_data['to_against_team']
        team_data['ThreePointMiss'] = team_data['three_missed_against_team']
        team_data['ThreePointMake'] = team_data['three_made_against_team']
        team_data['TwoPointMiss'] = team_data['two_missed_against_team']
        team_data['TwoPointMake'] = team_data['two_made_against_team']
        team_data['FTMiss'] = team_data['fta_against_team'] - team_data['ftm_against_team']
        team_data['FTMake'] = team_data['ftm_against_team']
    
        team_data['2ptOreb'] = np.where((team_data['oreb_against_team'] > 0) & (team_data['two_missed_against_team'] > 0), 
                                        np.minimum(team_data['oreb_against_team'], team_data['two_missed_against_team']), 0)
        team_data['2ptNotOreb'] = np.where((team_data['oreb_against_team'] == 0) & (team_data['two_missed_against_team'] > 0), 
                                           team_data['two_missed_against_team'], 0)
        team_data['3ptOreb'] = np.where((team_data['oreb_against_team'] > 0) & (team_data['three_missed_against_team'] > 0), 
                                        np.minimum(team_data['oreb_against_team'], team_data['three_missed_against_team']), 0)
        team_data['3ptNotOreb'] = np.where((team_data['oreb_against_team'] == 0) & (team_data['three_missed_against_team'] > 0), 
                                           team_data['three_missed_against_team'], 0)
    
        ft_missed = team_data['fta_against_team'] - team_data['ftm_against_team']
        team_data['FTOreb'] = np.where((team_data['oreb_against_team'] > 0) & (ft_missed > 0), 1, 0)
        team_data['FTNotOreb'] = 1 - team_data['FTOreb']
    
        states = ['Initial Possession', '3pt Attempt', '3pt Make', '3pt Miss', '2pt Attempt', '2pt Make', '2pt Miss', 
                  'Trip to FT Line', 'FT Attempt 1', 'FT Attempt 2', 'FT Make 1', 'FT Miss 1', 'FT Make 2', 'FT Miss 2', 'Turnover',
                  '2pt Oreb', '3pt Oreb', 'FT Oreb', '2pt NonOreb', '3pt NonOreb', 'FT NonOreb']
    
        transition_matrix = pd.DataFrame(0, index=states, columns=states)
    
        transition_matrix.loc['Initial Possession', 'Trip to FT Line'] = team_data['TripToFTline_outcome'].sum()
        transition_matrix.loc['Initial Possession', '3pt Attempt'] = team_data['ThreePointAttempt_outcome'].sum()
        transition_matrix.loc['Initial Possession', '2pt Attempt'] = team_data['TwoPointAttempt_outcome'].sum()
        transition_matrix.loc['Initial Possession', 'Turnover'] = team_data['Turnover_outcome'].sum()
    
        transition_matrix.loc['2pt Attempt', '2pt Make'] = team_data['TwoPointMake'].sum()
        transition_matrix.loc['2pt Attempt', '2pt Miss'] = team_data['TwoPointMiss'].sum()
    
        transition_matrix.loc['3pt Attempt', '3pt Make'] = team_data['ThreePointMake'].sum()
        transition_matrix.loc['3pt Attempt', '3pt Miss'] = team_data['ThreePointMiss'].sum()
    
        transition_matrix.loc['2pt Miss', '2pt Oreb'] = team_data['2ptOreb'].sum()
        transition_matrix.loc['2pt Miss', '2pt NonOreb'] = team_data['2ptNotOreb'].sum()
    
        transition_matrix.loc['3pt Miss', '3pt Oreb'] = team_data['3ptOreb'].sum()
        transition_matrix.loc['3pt Miss', '3pt NonOreb'] = team_data['3ptNotOreb'].sum()
    
        transition_matrix.loc['Trip to FT Line', 'FT Attempt 1'] = team_data['TripToFTline_outcome'].sum()
        transition_matrix.loc['FT Attempt 1', 'FT Make 1'] = team_data['FTMake'].sum()
        transition_matrix.loc['FT Attempt 1', 'FT Miss 1'] = team_data['FTMiss'].sum()
        transition_matrix.loc['FT Make 1', 'FT Attempt 2'] = team_data['FTMake'].sum()
        transition_matrix.loc['FT Miss 1', 'FT Attempt 2'] = team_data['FTMiss'].sum()
        transition_matrix.loc['FT Attempt 2', 'FT Make 2'] = team_data['FTMake'].sum()
        transition_matrix.loc['FT Attempt 2', 'FT Miss 2'] = team_data['FTMiss'].sum()
    
        transition_matrix.loc['FT Miss 2', 'FT Oreb'] = team_data['FTOreb'].sum()
        transition_matrix.loc['FT Miss 2', 'FT NonOreb'] = team_data['FTNotOreb'].sum()
    
        transition_matrix.loc['2pt Oreb', 'Initial Possession'] = team_data['2ptOreb'].sum()
        transition_matrix.loc['3pt Oreb', 'Initial Possession'] = team_data['3ptOreb'].sum()
        transition_matrix.loc['FT Oreb', 'Initial Possession'] = team_data['FTOreb'].sum()
    
        transition_matrix = transition_matrix.fillna(0)
    
        return transition_matrix
    
    # Calcuate percentage differences amongst home, nuetral and away, nuetral
    def calculate_percentage_difference(home_matrix, away_matrix):
        epsilon = 1e-9
        row_sums = home_matrix.sum(axis=1)
        
        home_matrix = home_matrix.div(row_sums, axis=0)
    
        row_sums2 = away_matrix.sum(axis=1)
        
        away_matrix = away_matrix.div(row_sums2, axis=0)
        
        percentage_difference_matrix = (home_matrix - away_matrix) / (away_matrix + epsilon)
        return percentage_difference_matrix.fillna(0) 
    
    # helper function to add in a column i have in the proper version of the transtion matrix
    def add_end_possession(transition_matrix):
        transition_matrix.loc['End Possession'] = 0
    
        transition_matrix['End Possession'] = 0
    
        
        return transition_matrix
    
    homeO_matrix = calculate_transition_matrix_team_offense(HomeOTeam, possessions_to_sim=20000)
    neutralOmatrix = calculate_transition_matrix_team_offense(OTeam, possessions_to_sim=20000)
    awayO_matrix = calculate_transition_matrix_team_offense(AwayOTeam, possessions_to_sim=20000)
    
    homeD_matrix = calculate_transition_matrix_team_defense(HomeDTeam, possessions_to_sim=20000)
    nuetralDmatrix = calculate_transition_matrix_team_defense(DTeam, possessions_to_sim=20000)
    awayD_matrix = calculate_transition_matrix_team_defense(AwayDTeam, possessions_to_sim=20000)
    
    # Differences betweeen Home and Nuetral and Away and Nuetral
    homeODiff = add_end_possession(calculate_percentage_difference(homeO_matrix, neutralOmatrix))
    homeDDiff = add_end_possession(calculate_percentage_difference(homeD_matrix, nuetralDmatrix))
    awayDDiff = add_end_possession(calculate_percentage_difference(awayD_matrix, nuetralDmatrix))
    awayODiff = add_end_possession(calculate_percentage_difference(awayO_matrix, neutralOmatrix))

    return homeODiff, homeDDiff, awayODiff, awayDDiff


# In[14]:


homeODiff, homeDDiff, awayODiff, awayDDiff = home_court_advantage(OffensePlayerDataNEW1, DefensePlayerDataNEW1)


# In[15]:


homeODiff.head()


# In[16]:


# Function which uses Elo ratings to create scaled probabilities
def calculate_elo_probability(rating, target_prob, target_rating=1500, scale_factor=1000):
    base_rating = target_rating + scale_factor * math.log10((1 / target_prob) - 1)
    exponent = (rating - base_rating) / scale_factor
    return 1 / (1 + math.pow(10, -exponent))

    
# Function which uses Elo ratings to create pace target number
def calculate_scaled_pace(pace_O, pace_D, target_value=71.9, reference_rating=1500):
    combined_pace = (pace_O + pace_D) / 2
    scaled_number = target_value * (reference_rating / combined_pace)
    return scaled_number


# Create offense Transtion matrix for 2 teams 
def calculate_transition_matrix_offense(elo_ratings_df, team1, team2, calcs):
    states = [
        'Initial Possession', '3pt Attempt', '3pt Make', '3pt Miss',
        '2pt Attempt', '2pt Make', '2pt Miss',
        'Trip to FT Line', 'FT Attempt 1', 'FT Attempt 2',
        'FT Make 1', 'FT Miss 1', 'FT Make 2', 'FT Miss 2',
        'Turnover', '2pt Oreb', '3pt Oreb', 'FT Oreb',
        '2pt NonOreb', '3pt NonOreb', 'FT NonOreb', 'End Possession']
    
    def handle_transition(current_state, next_state, transition_matrix):
        transition_matrix.loc[current_state, next_state] += 1
        return next_state

    def generate_team_matrix(team_df, calcs, total_possessions):
        transition_matrix = pd.DataFrame(0, index=states, columns=states)
    
        team_df['normalized_usage'] = team_df['usage_O'] / team_df['usage_O'].sum()

        team_ratings = {
            'to_O': (team_df['to_O'] * team_df['normalized_usage']).sum(),
            'fta_O': (team_df['fta_O'] * team_df['normalized_usage']).sum(),
            'two_attempt_O': (team_df['two_attempt_O'] * team_df['normalized_usage']).sum(),
            'three_attempt_O': (team_df['three_attempt_O'] * team_df['normalized_usage']).sum(),
            'three_made_O': (team_df['three_made_O'] * team_df['normalized_usage']).sum(),
            'two_made_O': (team_df['two_made_O'] * team_df['normalized_usage']).sum(),
            'ftm_O': (team_df['ftm_O'] * team_df['normalized_usage']).sum(),
            'oreb_O': (team_df['oreb_O'] * team_df['normalized_usage']).sum()}
    
        turnover_prob = calculate_elo_probability(team_ratings['to_O'], target_prob=0.12)
        ft_attempt_prob = calculate_elo_probability(team_ratings['fta_O'], target_prob=0.11)
        two_point_attempt_prob = calculate_elo_probability(team_ratings['two_attempt_O'], target_prob=0.41)
        three_point_attempt_prob = calculate_elo_probability(team_ratings['three_attempt_O'], target_prob=0.28)
    
        three_made_prob = calculate_elo_probability(team_ratings['three_made_O'], target_prob=0.37)
        two_made_prob = calculate_elo_probability(team_ratings['two_made_O'], target_prob=0.55)
        ft_made_prob = calculate_elo_probability(team_ratings['ftm_O'], target_prob=0.78)

        ft_oreb_prob = calculate_elo_probability(team_ratings['oreb_O'], target_prob=0.175)
        two_pt_oreb_prob = calculate_elo_probability(team_ratings['oreb_O'], target_prob=0.345)
        three_pt_oreb_prob = calculate_elo_probability(team_ratings['oreb_O'], target_prob=0.300)

        state_probs = {
            'Turnover': turnover_prob,
            'Trip to FT Line': ft_attempt_prob,
            '3pt Attempt': three_point_attempt_prob,
            '2pt Attempt': two_point_attempt_prob}

        total_prob = sum(state_probs.values())
        state_probs = {k: v / total_prob for k, v in state_probs.items()}

        for _ in range(calcs):
            current_state = 'Initial Possession'
            while current_state != 'End Possession':
                if current_state == 'Initial Possession':
                    next_state = np.random.choice(list(state_probs.keys()), p=list(state_probs.values()))
                    current_state = handle_transition(current_state, next_state, transition_matrix)
    
                elif current_state == '2pt Attempt':
                    outcome = np.random.choice(['2pt Make', '2pt Miss'], p=[two_made_prob, 1 - two_made_prob])
                    current_state = handle_transition(current_state, outcome, transition_matrix)
    
                    if outcome == '2pt Make':
                        current_state = handle_transition(current_state, 'End Possession', transition_matrix)
                    else:
                        if np.random.random() < two_pt_oreb_prob:
                            current_state = handle_transition(current_state, '2pt Oreb', transition_matrix)
                            current_state = handle_transition(current_state, 'Initial Possession', transition_matrix)
                        else:
                            current_state = handle_transition(current_state, '2pt NonOreb', transition_matrix)
                            current_state = handle_transition(current_state, 'End Possession', transition_matrix)
    
                elif current_state == '3pt Attempt':
                    outcome = np.random.choice(['3pt Make', '3pt Miss'], p=[three_made_prob, 1 - three_made_prob])
                    current_state = handle_transition(current_state, outcome, transition_matrix)
    
                    if outcome == '3pt Make':
                        current_state = handle_transition(current_state, 'End Possession', transition_matrix)
                    else:
                        if np.random.random() < three_pt_oreb_prob:
                            current_state = handle_transition(current_state, '3pt Oreb', transition_matrix)
                            current_state = handle_transition(current_state, 'Initial Possession', transition_matrix)
                        else:
                            current_state = handle_transition(current_state, '3pt NonOreb', transition_matrix)
                            current_state = handle_transition(current_state, 'End Possession', transition_matrix)
    
                elif current_state == 'Trip to FT Line':
                    current_state = handle_transition(current_state, 'FT Attempt 1', transition_matrix)
    
                    for attempt in ['FT Attempt 1', 'FT Attempt 2']:
                        outcome = np.random.choice([f'FT Make {attempt[-1]}', f'FT Miss {attempt[-1]}'],
                                                   p=[ft_made_prob, 1 - ft_made_prob])
                        current_state = handle_transition(current_state, outcome, transition_matrix)
    
                        if attempt == 'FT Attempt 2':
                            if outcome == 'FT Miss 2':
                                if np.random.random() < ft_oreb_prob:
                                    current_state = handle_transition(current_state, 'FT Oreb', transition_matrix)
                                    current_state = handle_transition(current_state, 'Initial Possession', transition_matrix)
                                else:
                                    current_state = handle_transition(current_state, 'FT NonOreb', transition_matrix)
                                    current_state = handle_transition(current_state, 'End Possession', transition_matrix)
                            else:
                                current_state = handle_transition(current_state, 'End Possession', transition_matrix)
                        else:
                            current_state = handle_transition(current_state, 'FT Attempt 2', transition_matrix)
    
                elif current_state == 'Turnover':
                    current_state = handle_transition(current_state, 'End Possession', transition_matrix)
    
        return transition_matrix

    team1_df = elo_ratings_df[elo_ratings_df['Team'] == team1]
    team2_df = elo_ratings_df[elo_ratings_df['Team'] == team2]

    pace_O_team1 = team1_df['pace_O'].mean()
    pace_D_team1 = team1_df['pace_D'].mean()
    pace_O_team2 = team2_df['pace_O'].mean()
    pace_D_team2 = team2_df['pace_D'].mean()

    scaled_pace_team = (calculate_scaled_pace(pace_O_team1, pace_D_team1) + calculate_scaled_pace(pace_O_team2, pace_D_team2)) / 2

    total_possessions_team = 5 * scaled_pace_team

    team1_matrix = generate_team_matrix(team1_df, calcs, total_possessions_team)
    team2_matrix = generate_team_matrix(team2_df, calcs, total_possessions_team)

    return team1_matrix, team2_matrix


# Create transition matrix for 2 teams defense
def calculate_transition_matrix_defense(elo_ratings_df, team1, team2, calcs):
    states = [
        'Initial Possession', '3pt Attempt', '3pt Make', '3pt Miss',
        '2pt Attempt', '2pt Make', '2pt Miss',
        'Trip to FT Line', 'FT Attempt 1', 'FT Attempt 2',
        'FT Make 1', 'FT Miss 1', 'FT Make 2', 'FT Miss 2',
        'Turnover', '2pt Oreb', '3pt Oreb', 'FT Oreb',
        '2pt NonOreb', '3pt NonOreb', 'FT NonOreb', 'End Possession']
    
    def handle_transition(current_state, next_state, transition_matrix):
        transition_matrix.loc[current_state, next_state] += 1
        return next_state

    def generate_team_matrix(team_df, calcs, total_possessions):
        transition_matrix = pd.DataFrame(0, index=states, columns=states)

        team_df['normalized_usage'] = team_df['usage_D'] / team_df['usage_D'].sum()

        team_ratings = {
            'to_D': (team_df['to_D'] * team_df['normalized_usage']).sum(),
            'fta_D': (team_df['fta_D'] * team_df['normalized_usage']).sum(),
            'two_attempt_D': (team_df['two_attempt_D'] * team_df['normalized_usage']).sum(),
            'three_attempt_D': (team_df['three_attempt_D'] * team_df['normalized_usage']).sum(),
            'three_made_D': (team_df['three_made_D'] * team_df['normalized_usage']).sum(),
            'two_made_D': (team_df['two_made_D'] * team_df['normalized_usage']).sum(),
            'ftm_D': (team_df['ftm_D'] * team_df['normalized_usage']).sum(),
            'oreb_D': (team_df['oreb_D'] * team_df['normalized_usage']).sum()}

        turnover_prob = calculate_elo_probability(team_ratings['to_D'], target_prob=0.12)
        ft_attempt_prob = calculate_elo_probability(team_ratings['fta_D'], target_prob=0.09)
        two_point_attempt_prob = calculate_elo_probability(team_ratings['two_attempt_D'], target_prob=0.41)
        three_point_attempt_prob = calculate_elo_probability(team_ratings['three_attempt_D'], target_prob=0.28)

        three_made_prob = calculate_elo_probability(team_ratings['three_made_D'], target_prob=0.37)
        two_made_prob = calculate_elo_probability(team_ratings['two_made_D'], target_prob=0.55)
        ft_made_prob = calculate_elo_probability(team_ratings['ftm_D'], target_prob=0.78)

        ft_oreb_prob = calculate_elo_probability(team_ratings['oreb_D'], target_prob=0.175)
        two_pt_oreb_prob = calculate_elo_probability(team_ratings['oreb_D'], target_prob=0.327)
        three_pt_oreb_prob = calculate_elo_probability(team_ratings['oreb_D'], target_prob=0.300)

        state_probs = {
            'Turnover': turnover_prob,
            'Trip to FT Line': ft_attempt_prob,
            '3pt Attempt': three_point_attempt_prob,
            '2pt Attempt': two_point_attempt_prob
        }

        total_prob = sum(state_probs.values())
        state_probs = {k: v / total_prob for k, v in state_probs.items()}

        for _ in range(calcs):
            current_state = 'Initial Possession'
            while current_state != 'End Possession':
                if current_state == 'Initial Possession':
                    next_state = np.random.choice(list(state_probs.keys()), p=list(state_probs.values()))
                    current_state = handle_transition(current_state, next_state, transition_matrix)
    
                elif current_state == '2pt Attempt':
                    outcome = np.random.choice(['2pt Make', '2pt Miss'], p=[two_made_prob, 1 - two_made_prob])
                    current_state = handle_transition(current_state, outcome, transition_matrix)
    
                    if outcome == '2pt Make':
                        current_state = handle_transition(current_state, 'End Possession', transition_matrix)
                    else:
                        if np.random.random() < two_pt_oreb_prob:
                            current_state = handle_transition(current_state, '2pt Oreb', transition_matrix)
                            current_state = handle_transition(current_state, 'Initial Possession', transition_matrix)
                        else:
                            current_state = handle_transition(current_state, '2pt NonOreb', transition_matrix)
                            current_state = handle_transition(current_state, 'End Possession', transition_matrix)
    
                elif current_state == '3pt Attempt':
                    outcome = np.random.choice(['3pt Make', '3pt Miss'], p=[three_made_prob, 1 - three_made_prob])
                    current_state = handle_transition(current_state, outcome, transition_matrix)
    
                    if outcome == '3pt Make':
                        current_state = handle_transition(current_state, 'End Possession', transition_matrix)
                    else:
                        if np.random.random() < three_pt_oreb_prob:
                            current_state = handle_transition(current_state, '3pt Oreb', transition_matrix)
                            current_state = handle_transition(current_state, 'Initial Possession', transition_matrix)
                        else:
                            current_state = handle_transition(current_state, '3pt NonOreb', transition_matrix)
                            current_state = handle_transition(current_state, 'End Possession', transition_matrix)
    
                elif current_state == 'Trip to FT Line':
                    current_state = handle_transition(current_state, 'FT Attempt 1', transition_matrix)
    
                    for attempt in ['FT Attempt 1', 'FT Attempt 2']:
                        outcome = np.random.choice([f'FT Make {attempt[-1]}', f'FT Miss {attempt[-1]}'],
                                                   p=[ft_made_prob, 1 - ft_made_prob])
                        current_state = handle_transition(current_state, outcome, transition_matrix)
    
                        if attempt == 'FT Attempt 2':
                            if outcome == 'FT Miss 2':
                                if np.random.random() < ft_oreb_prob:
                                    current_state = handle_transition(current_state, 'FT Oreb', transition_matrix)
                                    current_state = handle_transition(current_state, 'Initial Possession', transition_matrix)
                                else:
                                    current_state = handle_transition(current_state, 'FT NonOreb', transition_matrix)
                                    current_state = handle_transition(current_state, 'End Possession', transition_matrix)
                            else:
                                current_state = handle_transition(current_state, 'End Possession', transition_matrix)
                        else:
                            current_state = handle_transition(current_state, 'FT Attempt 2', transition_matrix)
    
                elif current_state == 'Turnover':
                    current_state = handle_transition(current_state, 'End Possession', transition_matrix)
    
        return transition_matrix

    team1_df = elo_ratings_df[elo_ratings_df['Team'] == team1]
    team2_df = elo_ratings_df[elo_ratings_df['Team'] == team2]

    pace_O_team1 = team1_df['pace_O'].mean()
    pace_D_team1 = team1_df['pace_D'].mean()
    pace_O_team2 = team2_df['pace_O'].mean()
    pace_D_team2 = team2_df['pace_D'].mean()

    scaled_pace_team = (calculate_scaled_pace(pace_O_team1, pace_D_team1) + calculate_scaled_pace(pace_O_team2, pace_D_team2)) / 2

    total_possessions_team = 5 * scaled_pace_team

    team1_matrix = generate_team_matrix(team1_df, calcs, total_possessions_team)
    team2_matrix = generate_team_matrix(team2_df, calcs, total_possessions_team)

    return team1_matrix, team2_matrix, scaled_pace_team


# In[17]:


# Functions to simulate possession, games, and multiple games and append to final dataset for results

# function to simulate one possession 
def simulate_possession(transition_matrix, initial_state='Initial Possession', max_steps=25):
    states = transition_matrix.index
    terminal_states = ['3pt Make', '2pt Make', 'FT Make 2', 'Turnover', 
                        '2pt NonOreb', '3pt NonOreb', 'FT NonOreb']
    state = initial_state
    possession_steps = [state]
    
    for _ in range(max_steps):
        transition_probs = transition_matrix.loc[state]
        next_state = np.random.choice(states, p=transition_probs)
        possession_steps.append(next_state)
        state = next_state
        
        if state in terminal_states:
            break
    
    return possession_steps


# count points scored on possession
def calculate_possession_stats(possession):
    stats = Counter(possession)
    points = 0
    if '3pt Make' in possession:
        points += 3
    if '2pt Make' in possession:
        points += 2
    if 'FT Make 1' in possession:
        points += 1
    if 'FT Make 2' in possession:
        points += 1
    stats['Points'] = points
    return stats


# simulate a game based on number of possessions in the game
def simulate_game(team_a_matrix, team_b_matrix, simmedpossessions2):
    team_a_stats = Counter()
    team_b_stats = Counter()

    full_possessions = int(simmedpossessions2)
    fractional_possession = simmedpossessions2 - full_possessions

    for _ in range(full_possessions):
        team_a_possession = simulate_possession(team_a_matrix)
        team_a_stats += calculate_possession_stats(team_a_possession)
        
        team_b_possession = simulate_possession(team_b_matrix)
        team_b_stats += calculate_possession_stats(team_b_possession)

    if fractional_possession > 0:
        team_a_fractional = simulate_possession(team_a_matrix)
        team_a_fractional_stats = calculate_possession_stats(team_a_fractional)
        for key in team_a_fractional_stats:
            team_a_stats[key] += team_a_fractional_stats[key] * fractional_possession
        
        team_b_fractional = simulate_possession(team_b_matrix)
        team_b_fractional_stats = calculate_possession_stats(team_b_fractional)
        for key in team_b_fractional_stats:
            team_b_stats[key] += team_b_fractional_stats[key] * fractional_possession
    
    return team_a_stats, team_b_stats


# team metrics from game simulation
def calculate_team_metrics(stats):
    metrics = {}
    metrics['3pt Attempts'] = stats['3pt Attempt']
    metrics['3pt Makes'] = stats['3pt Make']
    metrics['2pt Attempts'] = stats['2pt Attempt']
    metrics['2pt Makes'] = stats['2pt Make']
    metrics['FT Attempts'] = stats['FT Attempt 1'] + stats['FT Attempt 2']
    metrics['FT Makes'] = stats['FT Make 1'] + stats['FT Make 2']
    metrics['OREB'] = stats['2pt Oreb'] + stats['3pt Oreb'] + stats['FT Oreb'] 
    metrics['Non-OREB'] = stats['2pt NonOreb'] + stats['3pt NonOreb'] + stats['FT NonOreb']
    metrics['Points'] = stats['Points']
    metrics['Turnovers'] = stats['Turnover']
    metrics['Misses'] = stats['2pt Miss'] + stats['3pt Miss'] + stats['FT Attempt 2 Miss']
    metrics['Opp DREB'] = (stats['2pt Miss'] + stats['3pt Miss'] + stats['FT Attempt 2 Miss']) - (stats['2pt Oreb'] + stats['3pt Oreb'] + stats['FT Oreb'])



    metrics['3pt%'] = metrics['3pt Makes'] / metrics['3pt Attempts'] if metrics['3pt Attempts'] > 0 else 0
    metrics['2pt%'] = metrics['2pt Makes'] / metrics['2pt Attempts'] if metrics['2pt Attempts'] > 0 else 0
    metrics['FT%'] = metrics['FT Makes'] / metrics['FT Attempts'] if metrics['FT Attempts'] > 0 else 0
    metrics['FTA%'] = metrics['FT Attempts'] / (metrics['2pt Attempts'] + metrics['3pt Attempts']) if (metrics['2pt Attempts'] + metrics['3pt Attempts']) > 0 else 0
    metrics['OR%'] = metrics['OREB'] / (metrics['OREB'] + metrics['Opp DREB']) if (metrics['OREB'] + metrics['Opp DREB']) > 0 else 0

    return metrics


# simulate multiple games 
def run_multiple_games(team_a_matrix, team_b_matrix, num_games, simmedpossessions):
    results = []
    
    for _ in range(num_games):
        # Use simmedpossessions in the game simulation
        team_a_stats, team_b_stats = simulate_game(team_a_matrix, team_b_matrix, simmedpossessions)
        
        # Calculate team metrics
        team_a_metrics = calculate_team_metrics(team_a_stats)
        team_b_metrics = calculate_team_metrics(team_b_stats)
        
        # Assign each team's DREB metric to the opposing team's metrics
        team_a_metrics['DREB'] = team_b_metrics.get('Opp DREB', 0)  # Team A gets Team B's DREB as Opp DREB
        team_b_metrics['DREB'] = team_a_metrics.get('Opp DREB', 0)  # Team B gets Team A's DREB as Opp DREB
        
        results.append((team_a_metrics, team_b_metrics))
    
    return results, simmedpossessions
    

# take results of all games simulated to find derived means for each stat
import pandas as pd

def analyze_results(results, simmedpossessions, team_a_name, team_b_name):
    filtered_results = [game for game in results if game[0]['Points'] != game[1]['Points']]

    team_a_totals = {key: sum(game[0][key] for game in filtered_results) for key in results[0][0]}
    team_b_totals = {key: sum(game[1][key] for game in filtered_results) for key in results[0][1]}
    
    num_games = len(filtered_results)

    metrics_data = []

    if num_games == 0:  
        metrics_data.append({"Metric": "Average", team_a_name: None, team_b_name: None})
        metrics_data.append({"Metric": "Win Percentage", team_a_name: 0, team_b_name: 0})
        metrics_data.append({"Metric": "Tie Percentage", team_a_name: 1, team_b_name: None})
        metrics_data.append({"Metric": "Supremacy", team_a_name: None, team_b_name: None})
        metrics_data.append({"Metric": "Total", team_a_name: None, team_b_name: None})
    else:
        for key in team_a_totals.keys():
            team_a_average = team_a_totals[key] / num_games
            team_b_average = team_b_totals[key] / num_games if key in team_b_totals else None
            metrics_data.append({"Metric": key, team_a_name: team_a_average, team_b_name: team_b_average})

        team_a_wins = sum(game[0]['Points'] > game[1]['Points'] for game in filtered_results)
        team_b_wins = sum(game[1]['Points'] > game[0]['Points'] for game in filtered_results)
        
        win_pct_a = team_a_wins / num_games if num_games > 0 else 0
        win_pct_b = team_b_wins / num_games if num_games > 0 else 0

        metrics_data.append({"Metric": "Win Percentage", team_a_name: win_pct_a, team_b_name: win_pct_b})

        total_team_a_points = sum(game[0]['Points'] for game in filtered_results)
        total_team_b_points = sum(game[1]['Points'] for game in filtered_results)
        
        sup_team_a = (total_team_a_points - total_team_b_points) / num_games
        sup_team_b = (total_team_b_points - total_team_a_points) / num_games
        
        metrics_data.append({"Metric": "Supremacy", team_a_name: sup_team_a, team_b_name: sup_team_b})

        total_points = (total_team_a_points + total_team_b_points) / num_games
        metrics_data.append({"Metric": "Total", team_a_name: total_points, team_b_name: total_points})
        metrics_data.append({"Metric": "Possessions", team_a_name: simmedpossessions, team_b_name: simmedpossessions})

        # Adding new metrics
        money_a = 1 / win_pct_a if win_pct_a > 0 else None
        money_b = 1 / win_pct_b if win_pct_b > 0 else None
        metrics_data.append({"Metric": "Money", team_a_name: money_a, team_b_name: money_b})

        spread_a = round(-sup_team_a * 2) / 2  # Ensures rounding to nearest 0.5
        spread_b = round(-sup_team_b * 2) / 2
        metrics_data.append({"Metric": "Spread", team_a_name: spread_a, team_b_name: spread_b})

        total_adjusted = round(total_points * 1.005 * 2) / 2  # Rounds to nearest 0.5
        metrics_data.append({"Metric": "Total Adjusted", team_a_name: total_adjusted, team_b_name: total_adjusted})

    results_df = pd.DataFrame(metrics_data)

    return results_df


def simulate_matchup(home_team,away_team,HFA, number_of_simulations, possessionAdjust, teamsDF1):
    team1O, team2O = calculate_transition_matrix_offense(teamsDF1, home_team,away_team, calcs=25000)
    team1D, team2D, simmedpossessions = calculate_transition_matrix_defense(teamsDF1, home_team,away_team, calcs=25000)
    team1 = team1O + team2D
    team2 = team2O + team1D
    team1 = team1 * (1 + (HFA * (homeODiff + awayDDiff)))
    team2 = team2 * (1 + (HFA * (awayODiff + homeDDiff)))
    row_sums = team1.sum(axis=1)
    row_sums2 = team2.sum(axis=1)
    HomeTeamMatrix = team1.div(row_sums, axis=0).fillna(0)
    AwayTeamMatrix = team2.div(row_sums2, axis=0).fillna(0)
    
    results, simmedpossessionsA = run_multiple_games(HomeTeamMatrix, AwayTeamMatrix, number_of_simulations, simmedpossessions + possessionAdjust)
    box_score = analyze_results(results,simmedpossessionsA, home_team, away_team)

    return box_score.round(3)


# In[18]:


# Determine who will be playing upcoming game for each team
def assess_teams(OffensePlayerDataNEW1,elo_combined_df):
    
    # Assess the players who are active and project the number of possessions each player will have based on rolling averages.
    PlayerTeams = OffensePlayerDataNEW1[['PlayerID', 'Team', 'Season']]
    
    # Sort by Season in descending order and take the first occurrence of each PlayerID
    latest_teams = (PlayerTeams
        .sort_values('Season', ascending=False)
        .groupby('PlayerID')
        .first()
        .reset_index()[['PlayerID', 'Team']])
    
    elo_combined_df2 = elo_combined_df.merge(PlayerTeams,
                          left_on='PlayerID', right_on=['PlayerID'],how='left').drop_duplicates().dropna()
    
    MostRecentSeason = OffensePlayerDataNEW1[OffensePlayerDataNEW1['Season'] == OffensePlayerDataNEW1['Season'].max()]
    TeamMostRecentGame = MostRecentSeason.groupby(by='Team_x')['Gamecode'].max().reset_index()
    TeamMostRecentGame['MostRecentGame'] = TeamMostRecentGame['Gamecode']
    
    avgPossessionsPerPlayer = MostRecentSeason.groupby(by=['PlayerID','Player','Team_x','Gamecode']).size().reset_index().sort_values(by=['PlayerID','Team_x','Gamecode'],
                                                                                                                ascending=[True,True,False])
    avgPossessionsPerPlayer['Order'] = avgPossessionsPerPlayer.groupby(['PlayerID']).cumcount() + 1
    
    avgPossessionsPerPlayer = avgPossessionsPerPlayer[avgPossessionsPerPlayer['Order'] <= 3]
    avgPossessionsPerPlayer['PossessionCount'] = avgPossessionsPerPlayer[0]
    
    avgPossessionsPerPlayer = avgPossessionsPerPlayer.merge(TeamMostRecentGame,left_on=['Team_x','Gamecode'],right_on=['Team_x','Gamecode'],how='left')
    avgPossessionsPerPlayer['PlayedInMostRecentGame'] = np.where(avgPossessionsPerPlayer['MostRecentGame'] >= 0,1,0)
    
    PlayerPossessionsToSim = avgPossessionsPerPlayer.groupby(by=['PlayerID','Player','Team_x']).agg({'PossessionCount':'mean',
                                                                                     'PlayedInMostRecentGame':'max'}).reset_index()
    
    
    teamsDF = elo_combined_df2.merge(PlayerPossessionsToSim[['PlayerID','PossessionCount','PlayedInMostRecentGame']], on='PlayerID',how='left')

    return teamsDF


# function to add or remove a player from a team
def update_or_remove_player_data(players_data, df):
    # If players_data is empty, return the entire DataFrame
    if not players_data:
        return df
    
    df_copy = df.copy()
    
    for player_info in players_data:
        player_name = player_info['Player']
        
        # Check if the action is to remove the player
        if player_info.get('Action') == 'remove':
            # Just remove exact player name match
            rows_before = len(df_copy)
            df_copy = df_copy[df_copy['Player'] != player_name]
            rows_removed = rows_before - len(df_copy)
            if rows_removed > 0:
                print(f"Removed {player_name} from the DataFrame.")
            else:
                print(f"Player {player_name} not found in the DataFrame.")
        else:
            # Get the player's original data from the source DataFrame
            player_data = df[df['Player'] == player_name]
            
            if not player_data.empty:
                new_player_data = player_data.copy()
                
                # Update only the specified fields
                if player_info.get('PossessionCount') is not None:
                    new_player_data['PossessionCount'] = player_info['PossessionCount']
                if player_info.get('Team') is not None:
                    new_player_data['Team'] = player_info['Team']
                if player_info.get('PlayedInMostRecentGame') is not None:
                    new_player_data['PlayedInMostRecentGame'] == 1
                
                # Add the modified player data to the DataFrame
                df_copy = pd.concat([df_copy, new_player_data], ignore_index=True)
                print(f"Added {player_name} to {player_info['Team']}.")
            else:
                print(f"Player {player_name} not found in the DataFrame.")
    
    # Remove duplicates but keep the last occurrence (the new team entry)
    df_copy = df_copy.drop_duplicates(subset=['Player'], keep='last')
    
    return df_copy
    


# In[19]:


teamsDF = assess_teams(OffensePlayerDataNEW1,elo_combined_df)


# In[20]:


teamsDF.head()


# In[21]:


def run_full_simuluation (home_team, away_team, HFA, players_to_update, number_of_simulations, possession_adjust,
                         teamsDF, homeusage_for, awayusage_for, homeusage_against, awayusage_against):

    '''
    Returns simulated team level stats and player level box score.
    
    Parameters:
        home_team (str): Team code (e.g., 'BAR', 'IST', 'ASV')
        away_team (str): Team code (e.g., 'MAD', 'TEL', 'RED')
        players_to_update (list): List of dictionaries to add or remove players
        number_of_simulations (int): Number of simulations (default 15000)
        HFA (float): Home court advantage (default 0.8)
        possession_adjust (float): Possession adjustment (e.g., to slow the game down by 1 possession, -1.)
    '''
    
    teamsDF1 = update_or_remove_player_data(players_to_update, teamsDF)
    teamsDF1 = teamsDF1[(teamsDF1['PlayedInMostRecentGame'] == 1) & (teamsDF1['Season'] == teamsDF1['Season'].max())]
    
    SimmedGameStats = simulate_matchup(home_team, away_team, HFA, number_of_simulations, possession_adjust, teamsDF1)

    playerstats1A = pd.concat([homeusage_for,awayusage_for])
    playerstats13 = (playerstats1A.sort_values(['PlayerID', 'Season', 'Gamecode', 'Possession'], 
                                            ascending=[True, False, False, False]))
    
    # Create decay weights for each possession
    def calculate_decay_weights(group, decay_factor=0.99):
        indices = np.arange(len(group))
        weights = np.power(decay_factor, indices)
        # Normalize weights to sum to 1
        weights = weights / weights.sum()
        return weights
    
    # Apply weighted average
    def weighted_mean(group, col_name, weights):
        return np.average(group[col_name], weights=weights)
    
    # Group by player and calculate weighted stats
    playerstats52 = (playerstats13.groupby(['Team', 'PlayerID'])
                     .apply(lambda x: pd.Series({
                         'fta': weighted_mean(x, 'fta_player', calculate_decay_weights(x)),
                         'threefga': weighted_mean(x, 'threefga_player', calculate_decay_weights(x)),
                         'twofga': weighted_mean(x, 'twoefga_player', calculate_decay_weights(x)),
                         'twofgm': weighted_mean(x, 'twoefgm_player', calculate_decay_weights(x)),
                         'threefgm': weighted_mean(x, 'threefgm_player', calculate_decay_weights(x)),
                         'ftmade': weighted_mean(x, 'ftm_player', calculate_decay_weights(x)),
                         'assist': weighted_mean(x, 'assist_player', calculate_decay_weights(x)),
                         'to': weighted_mean(x, 'to_player', calculate_decay_weights(x)),
                         'oreb': weighted_mean(x, 'oreb_player', calculate_decay_weights(x))
                     }))
                     .reset_index())
    
    playerstats2A = pd.concat([homeusage_against,awayusage_against])
    playerstats23 = (playerstats2A.sort_values(['PlayerID', 'Season', 'Gamecode', 'OppPossession'], 
                                            ascending=[True, False, False, False]))
    playerstats22 = playerstats23.groupby(by=['Team','PlayerID']).agg(dreb=('dreb_player','mean'),
                                                                     ).reset_index()
    playerstats12 = pd.merge(playerstats52,playerstats22)
    
    averagesShooting = playerstats12[['fta', 'threefga', 'twofga', 'twofgm', 'threefgm', 'ftmade', 'assist', 'to', 'oreb','dreb']].mean()
    
    weight_ft = .3  # Weight for free throw percentage
    weight_two = .25  # Weight for two-point percentage
    weight_three = .4 # Weight for three-point percentage
    
    # Regressed shooting percentages
    playerstats12['ft%'] = ((playerstats12['ftmade'] / playerstats12['fta']) * playerstats12['fta'] +
                                      (averagesShooting['ftmade'] / averagesShooting['fta']) * weight_ft) / \
                                      (playerstats12['fta'] + weight_ft)
    
    playerstats12['two%'] = ((playerstats12['twofgm'] / playerstats12['twofga']) * playerstats12['twofga'] +
                                       (averagesShooting['twofgm'] / averagesShooting['twofga']) * weight_two) / \
                                       (playerstats12['twofga'] + weight_two)
    
    playerstats12['three%'] = ((playerstats12['threefgm'] / playerstats12['threefga']) * playerstats12['threefga'] +
                                         (averagesShooting['threefgm'] / averagesShooting['threefga']) * weight_three) / \
                                         (playerstats12['threefga'] + weight_three)
    
    playerstats12['points'] = playerstats12['threefgm']*3 + playerstats12['twofgm']*2 + playerstats12['ftmade']
    
    PlayerPossessionsToSimWithAttempts = teamsDF1.merge(playerstats12, left_on=['Team','PlayerID'], right_on=['Team','PlayerID'], how='left')
    
    PlayerPossessionsToSimWithAttempts = PlayerPossessionsToSimWithAttempts[PlayerPossessionsToSimWithAttempts['Team'].isin([SimmedGameStats.columns[1],SimmedGameStats.columns[2]])]
    
    SimmedGameStats2 = SimmedGameStats.set_index('Metric')
    
    df_inverted = SimmedGameStats2.transpose()
    
    InitialEstimates = PlayerPossessionsToSimWithAttempts.merge(df_inverted, left_on='Team',right_on=df_inverted.index,how='left')
    
    InitialEstimates['PlayerFTA'] = InitialEstimates['fta']*InitialEstimates['PossessionCount']
    InitialEstimates['Player2FGA'] = InitialEstimates['twofga']*InitialEstimates['PossessionCount']
    InitialEstimates['Player3FGA'] = InitialEstimates['threefga']*InitialEstimates['PossessionCount']
    InitialEstimates['PlayerAssist'] = InitialEstimates['assist']*InitialEstimates['PossessionCount']
    InitialEstimates['PlayerTO'] = InitialEstimates['to']*InitialEstimates['PossessionCount']
    InitialEstimates['PlayerOreb'] = InitialEstimates['oreb']*InitialEstimates['PossessionCount']
    InitialEstimates['PlayerPts'] = InitialEstimates['points']*InitialEstimates['PossessionCount']
    InitialEstimates['PlayerDreb'] = InitialEstimates['dreb']*InitialEstimates['PossessionCount']
    
    InitialEstimatesTeamTotals  = InitialEstimates.groupby(by='Team').agg(fta2=('PlayerFTA', 'sum'),
                                            twofga2 = ('Player2FGA','sum'),
                                            threefga2 = ('Player3FGA','sum'),
                                                                          points2 = ('PlayerPts','sum'),
                                                                         assist2 = ('PlayerAssist','sum'),
                                                                         to2 = ('PlayerTO','sum'),
                                                                         oreb2 = ('PlayerOreb','sum'),                                                                 
                                                                         dreb2 = ('PlayerDreb','sum'),
                                                                         ).reset_index()
    
    NormalizedEstimates = InitialEstimates.merge(InitialEstimatesTeamTotals,left_on='Team',right_on='Team',how='left')
    NormalizedEstimates['FTA'] = (NormalizedEstimates['FT Attempts']/NormalizedEstimates['fta2'])*NormalizedEstimates['PlayerFTA']
    NormalizedEstimates['2FGA'] = (NormalizedEstimates['2pt Attempts']/NormalizedEstimates['twofga2'])*NormalizedEstimates['Player2FGA']
    NormalizedEstimates['3FGA'] = (NormalizedEstimates['3pt Attempts']/NormalizedEstimates['threefga2'])*NormalizedEstimates['Player3FGA']
    NormalizedEstimates['TO'] = (NormalizedEstimates['Turnovers']/NormalizedEstimates['to2'])*NormalizedEstimates['PlayerTO']
    NormalizedEstimates['OREB'] = (NormalizedEstimates['OREB']/NormalizedEstimates['oreb2'])*NormalizedEstimates['PlayerOreb']
    NormalizedEstimates['DREB'] = ((NormalizedEstimates['DREB']*.93)/NormalizedEstimates['dreb2'])*NormalizedEstimates['PlayerDreb']
    NormalizedEstimates['REB'] = NormalizedEstimates['OREB'] + NormalizedEstimates['DREB']
    
    
    NormalizedEstimates['PlayerFTM_initial'] = NormalizedEstimates['ft%']*NormalizedEstimates['FTA']
    NormalizedEstimates['Player2FGM_initial'] = NormalizedEstimates['two%']*NormalizedEstimates['2FGA']
    NormalizedEstimates['Player3FGM_initial'] = NormalizedEstimates['three%']*NormalizedEstimates['3FGA']
    
    NormalizedEstimates['PlayerFTM_initial'] = NormalizedEstimates['PlayerFTM_initial'].fillna(0)
    NormalizedEstimates['Player2FGM_initial'] = NormalizedEstimates['Player2FGM_initial'].fillna(0)
    NormalizedEstimates['Player3FGM_initial'] = NormalizedEstimates['Player3FGM_initial'].fillna(0)
    
    normtotals = NormalizedEstimates.groupby(by='Team').agg(ftm2=('PlayerFTM_initial', 'sum'),
                                            twofgm2 = ('Player2FGM_initial','sum'),
                                            threefgm2 = ('Player3FGM_initial','sum'),).reset_index()
    
    NormalizedEstimates2 = NormalizedEstimates.merge(normtotals,left_on='Team',right_on='Team',how='left')
    NormalizedEstimates2['FTM'] = (NormalizedEstimates2['FT Makes']/NormalizedEstimates2['ftm2'])*NormalizedEstimates2['PlayerFTM_initial']
    NormalizedEstimates2['2FGM'] = (NormalizedEstimates2['2pt Makes']/NormalizedEstimates2['twofgm2'])*NormalizedEstimates2['Player2FGM_initial']
    NormalizedEstimates2['3FGM'] = (NormalizedEstimates2['3pt Makes']/NormalizedEstimates2['threefgm2'])*NormalizedEstimates2['Player3FGM_initial']
    
    NormalizedEstimates2['PTS'] = (NormalizedEstimates2['3FGM']*3) + (NormalizedEstimates2['2FGM']*2) + (NormalizedEstimates2['FTM'])
    
    NormalizedEstimates2['2PT%'] = NormalizedEstimates2['2FGM'] / NormalizedEstimates2['2FGA']
    NormalizedEstimates2['FT%'] = NormalizedEstimates2['FTM'] / NormalizedEstimates2['FTA']
    NormalizedEstimates2['3PT%'] = NormalizedEstimates2['3FGM'] / NormalizedEstimates2['3FGA']

    
    possessionTime = 2400/SimmedGameStats.iloc[21][1]
    NormalizedEstimates2['MIN'] = round((NormalizedEstimates2['PossessionCount'] * possessionTime)/60,1)
    SimmedBoxScore = NormalizedEstimates2[['Team','PlayerID','Player','MIN','FTM','FTA','FT%','2FGM','2FGA','2PT%','3FGM','3FGA','3PT%','PTS','TO','OREB','DREB','REB']].drop_duplicates()
    
    SimmedBoxScore = SimmedBoxScore.fillna(0).round(2)
    
    
        # Split into two teams
    SimmedBoxScoreHome = SimmedBoxScore[SimmedBoxScore['Team'] == home_team].sort_values('PTS', ascending=False)
    SimmedBoxScoreAway = SimmedBoxScore[SimmedBoxScore['Team'] == away_team].sort_values('PTS', ascending=False)
    
    return SimmedGameStats, SimmedBoxScore, SimmedBoxScoreHome, SimmedBoxScoreAway


# In[ ]:





# In[ ]:





# In[ ]:





# In[28]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_team_code(team_name):
    team_codes = {
        'Zalgiris Kaunas': 'ZAL',
        'FC Bayern Munich': 'MUN',
        'Maccabi Playtika Tel Aviv': 'TEL',
        'ALBA Berlin': 'BER',
        'Paris Basketball': 'PRS',
        'LDLC ASVEL Villeurbanne': 'ASV',
        'EA7 Emporio Armani Milan': 'MIL',
        'Panathinaikos AKTOR Athens': 'PAN',
        'Baskonia Vitoria-Gasteiz': 'BAS',
        'FC Barcelona': 'BAR',
        'Fenerbahce Beko Istanbul': 'ULK',
        'Virtus Segafredo Bologna': 'VIR',
        'AS Monaco': 'MCO',
        'Real Madrid': 'MAD',
        'Olympiacos Piraeus': 'OLY',
        'Anadolu Efes Istanbul': 'IST',
        'Partizan Mozzart Bet Belgrade': 'PAR',
        'Crvena Zvezda Meridianbet Belgrade': 'RED'
    }
    return team_codes.get(team_name, '')

def get_euroleague_games_selenium(round_number):
    # Setup Chrome webdriver
    options = webdriver.ChromeOptions()
    # Uncomment the next line to run in background
    # options.add_argument('--headless')  
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to the specific round page
        driver.get(f"https://www.euroleaguebasketball.net/en/euroleague/game-center/?round={round_number}&season=E2024")
        
        # Wait for page to load
        time.sleep(5)  # Give time for dynamic content to load
        
        # Optional: Look for and click cookie consent
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All')]"))
            )
            cookie_button.click()
            time.sleep(2)  # Wait after clicking
        except Exception as e:
            print(f"No cookie consent found or unable to click: {e}")
        
        # Get page source
        page_source = driver.page_source
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Try to find round information
        round_element = soup.find('span', text=lambda t: t and 'Round' in t)
        round_text = round_element.text.strip() if round_element else f'Round {round_number}'
        
        # Find the season information (Regular Season)
        season_element = soup.select_one('div[class*="seasonFilters"] button:nth-child(2)')
        season_text = season_element.text.strip() if season_element else 'Regular Season'
        
        # Combine season and round text
        full_round_text = f"{season_text} {round_text}"
        
        # Find all game articles
        game_articles = soup.find_all('article')
        
        matches = []
        for article in game_articles:
            game_span = article.find('span', class_='visually-hidden_wrap__Ob8t3')
            if game_span and game_span.text.strip().startswith('game '):
                teams = game_span.text.strip()[5:].split(' vs ')
                if len(teams) == 2:
                    home_team = teams[1].strip()
                    away_team = teams[0].strip()
                    
                    # Get info div containing time and arena
                    info_div = article.select_one('div[class*="gameCard"] > div > div')
                    if info_div:
                        game_time = info_div.find('time').text.strip() if info_div.find('time') else ''
                        arena_span = article.select_one('div[class*="gameCard"] > div > div > span')
                        arena = arena_span.text.strip() if arena_span else ''
                    
                    matches.append({
                        'Home': home_team,
                        'Away': away_team,
                        'Home_Code': get_team_code(home_team),
                        'Away_Code': get_team_code(away_team),
                        'Matchup': f"{away_team} @ {home_team}",
                        'Time': game_time,
                        'Arena': arena,
                        'Round': full_round_text
                    })
        
        return pd.DataFrame(matches)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()
    
    finally:
        # Always close the browser
        driver.quit()

# Team logo mapping
team_logo_mapping_2024_2025 = {
    "ZAL": "https://media-cdn.incrowdsports.com/0aa09358-3847-4c4e-b228-3582ee4e536d.png?width=180&height=180&resizeType=fill&format=webp",
    "MAD": "https://media-cdn.incrowdsports.com/601c92bf-90e4-4b43-9023-bd6946e34143.png?crop=244:244:nowe:0:0",
    "BAR": "https://media-cdn.incrowdsports.com/35dfa503-e417-481f-963a-bdf6f013763e.png?crop=511%3A511%3Anowe%3A1%3A0",
    "OLY": "https://media-cdn.incrowdsports.com/789423ac-3cdf-4b89-b11c-b458aa5f59a6.png?crop=512:512:nowe:0:0",
    "PAN": "https://media-cdn.incrowdsports.com/e3dff28a-9ec6-4faf-9d96-ecbc68f75780.png?crop=512%3A512%3Anowe%3A0%3A0",
    "ULK": "https://media-cdn.incrowdsports.com/f7699069-e207-43b7-8c8e-f61e39cb0141.png?crop=512:512:nowe:0:0",
    "IST": "https://media-cdn.incrowdsports.com/8ea8cec7-d8f7-45f4-a956-d976b5867610.png?crop=463:463:nowe:22:25",
    "TEL": "https://media-cdn.incrowdsports.com/5c55ef14-29df-4328-bd52-a7a64c432350.png?width=180&height=180&resizeType=fill&format=webp",
    "MIL": "https://media-cdn.incrowdsports.com/8154f184-c61a-4e7f-b14d-9d802e35cb95.png?width=180&height=180&resizeType=fill&format=webp",
    "MUN": "https://media-cdn.incrowdsports.com/817b0e58-d595-4b09-ab0b-1e7cc26249ff.png?crop=192%3A192%3Anowe%3A0%3A0",
    "ASV": "https://media-cdn.incrowdsports.com/e33c6d1a-95ca-4dbc-b8cb-0201812104cc.png?width=180&height=180&resizeType=fill&format=webp",
    "BER": "https://media-cdn.incrowdsports.com/ccc34858-22b0-47dc-904c-9940b0a16ff3.png?width=180&height=180&resizeType=fill&format=webp",
    "RED": "https://media-cdn.incrowdsports.com/26b7b829-6e40-4da9-a297-abeedb6441df.svg",
    "BAS": "https://media-cdn.incrowdsports.com/e324a6af-2a72-443e-9813-8bf2d364ddab.png",
    "VIR": "https://media-cdn.incrowdsports.com/4af5e83b-f2b5-4fba-a87c-1f85837a508a.png?crop=512%3A512%3Anowe%3A0%3A0",
    "PAR": "https://media-cdn.incrowdsports.com/ead471d0-93d8-4fb9-bfec-41bb767c828d.png",
    "PRS": "https://media-cdn.incrowdsports.com/a033e5b3-0de7-48a3-98d9-d9a4b9df1f39.png?width=180&height=180&resizeType=fill&format=webp",
    "MCO": "https://media-cdn.incrowdsports.com/89ed276a-2ba3-413f-8ea2-b3be209ca129.png?crop=512:512:nowe:0:0",
}

# Process each round (29, 30, 31)
for round_number in [32, 33, 34]:
    print(f"\n--- Processing Round {round_number} ---\n")
    
    # Get games for the current round
    games = get_euroleague_games_selenium(round_number)
    
    # Check if games were found
    if games.empty:
        print(f"No games found for Round {round_number}. Skipping to next round.")
        continue
    
    # Process simulations for this round
    all_simulations = []
    
    # Iterate through each game in the DataFrame
    for index, game in games.iterrows():
        updated_players = []
        
        # Set HFA based on home team
        home_team_hfa = 0.8 if game['Home_Code'] != 'TEL' else 0
        
        print(f"Simulating: {game['Away']} @ {game['Home']}")
        
        SimmedTeamStats, SimmedBoxScore, SimmedBoxScoreTeam1, SimmedBoxScoreTeam2 = run_full_simuluation(
            home_team=game['Home_Code'],
            away_team=game['Away_Code'], 
            HFA=home_team_hfa, 
            players_to_update=updated_players, 
            number_of_simulations=20000, 
            possession_adjust=0,
            teamsDF=teamsDF,
            homeusage_for=homeusage_for,
            awayusage_for=awayusage_for,
            homeusage_against=homeusage_against,
            awayusage_against=awayusage_against,
        )
        
        # Add print statement to show home and away teams after simulation
        print(f"Simulation completed: {game['Home']} (Home) vs {game['Away']} (Away)")
        
        # Create a dictionary with simulation results and game details
        simulation_result = {
            'Matchup': game['Matchup'],
            'Home_Team': game['Home'],
            'Away_Team': game['Away'],
            'Home_Code': game['Home_Code'],
            'Away_Code': game['Away_Code'],
            'Time': game['Time'],
            'Arena': game['Arena'],
            'Round': game['Round'],
            'SimmedTeamStats': SimmedTeamStats,
            'SimmedBoxScore': SimmedBoxScore,
            'SimmedBoxScoreTeam1': SimmedBoxScoreTeam1,
            'SimmedBoxScoreTeam2': SimmedBoxScoreTeam2
        }
        
        # Append the simulation result to the list
        all_simulations.append(simulation_result)
    
    # Convert the list of simulation results to a DataFrame
    simulation_results_df = pd.DataFrame(all_simulations)
    
    # Add logos
    simulation_results_df['Home_Logo'] = simulation_results_df['Home_Code'].map(team_logo_mapping_2024_2025)
    simulation_results_df['Away_Logo'] = simulation_results_df['Away_Code'].map(team_logo_mapping_2024_2025)
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a 'data' directory if it doesn't exist
    os.makedirs(os.path.join(script_dir, 'data'), exist_ok=True)
    
    # Full path to the pickle file
    pickle_path = os.path.join(script_dir, 'data', f'euroleague_simulations_round_{round_number}.pkl')
    
    # Save the DataFrame
    with open(pickle_path, 'wb') as f:
        pickle.dump(simulation_results_df, f)
    
    print(f"Simulation results for Round {round_number} saved to {pickle_path}")
    print(f"Found {len(simulation_results_df)} games for Round {round_number}")

# In[ ]:





# In[ ]:




