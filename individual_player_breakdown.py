#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
    
    print("10")
    
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

    return OffensePlayerDataNEW1, DefensePlayerDataNEW1

