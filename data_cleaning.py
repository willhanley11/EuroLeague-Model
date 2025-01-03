#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

def clean_playbyplay_data(playbyplay_data, boxscore_data, shot_data):
    
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
    alldata = alldata[(abs(alldata['POINTS_A'] - alldata['POINTS_B']) <= 20) | (alldata['Period'] < 4)]
    
    # Return Clean Play by Play Dataset
    return alldata[['Season','Phase','Round','Gamecode','HomeTeam','AwayTeam','Period','Clock','NumberOfPlay',
                    'Team','PlayerId','PlayerName','PlayType','Action','PlayInfo','PointsScored','ShotCoord_X',
                    'ShotCoord_Y','ShotZone','FastBreak','SecondChance','PointsOffTurnover','PeriodSecondsElapsed',
                    'HomePossession','AwayPossession','HomePlayersOnCourt','AwayPlayersOnCourt','FoulOffBall','And1','TOSteal',
                    'LastPossessionOfQuarter','And1Assisted','MissedFTOreb','POTENTIALERROR','POTENTIALERROR2','POTENTIALERROR3',
                    'UnsportsFT','techFT','UnsportsBasket','Last_FT']].sort_values(by=['Season','Gamecode','NumberOfPlay'],ascending=[True,True,True])

