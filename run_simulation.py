#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
        teamsDF: teamsDF
        homeusage_for: homeusage_for
        awayusage_for: awayusage_for
        homeusage_against: homeusage_against
        awayusage_against: awayusage_against
    '''
    
    teamsDF1 = update_or_remove_player_data(players_to_update, teamsDF)
    teamsDF1 = teamsDF1[teamsDF1['PlayedInMostRecentGame'] == 1]
    
    SimmedGameStats = simulate_matchup(home_team, away_team, HFA, number_of_simulations, possession_adjust)

    playerstats1A = pd.concat([homeusage_for,awayusage_for])
    playerstats13 = (playerstats1A.sort_values(['PlayerID', 'Season', 'Gamecode', 'Possession'], 
                                            ascending=[True, False, False, False]))
    
    # Create decay weights for each possession
    def calculate_decay_weights(group, decay_factor=0.98):
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
    NormalizedEstimates['ORB'] = (NormalizedEstimates['OREB']/NormalizedEstimates['oreb2'])*NormalizedEstimates['PlayerOreb']
    NormalizedEstimates['DRB'] = ((NormalizedEstimates['DREB']*.93)/NormalizedEstimates['dreb2'])*NormalizedEstimates['PlayerDreb']
    NormalizedEstimates['TRB'] = NormalizedEstimates['ORB'] + NormalizedEstimates['DRB']
    
    
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
    
    NormalizedEstimates2['Pts'] = (NormalizedEstimates2['3FGM']*3) + (NormalizedEstimates2['2FGM']*2) + (NormalizedEstimates2['FTM'])
    
    NormalizedEstimates2['2PT%'] = NormalizedEstimates2['2FGM'] / NormalizedEstimates2['2FGA']
    NormalizedEstimates2['FT%'] = NormalizedEstimates2['FTM'] / NormalizedEstimates2['FTA']
    NormalizedEstimates2['3PT%'] = NormalizedEstimates2['3FGM'] / NormalizedEstimates2['3FGA']
    
    possessionTime = 2400/SimmedGameStats.iloc[21][1]
    NormalizedEstimates2['Minutes'] = round((NormalizedEstimates2['PossessionCount'] * possessionTime)/60,1)
    
    SimmedBoxScore = NormalizedEstimates2[['Team','PlayerID','Player','Minutes','FTM','FTA','FT%','2FGM','2FGA','2PT%','3FGM','3FGA','3PT%','Pts','TO','ORB','DRB','TRB']].drop_duplicates()
    
    SimmedBoxScore = SimmedBoxScore.fillna(0).round(2).sort_values(by=['Team','Pts'], ascending=[False,False])
    
    return SimmedGameStats, SimmedBoxScore

