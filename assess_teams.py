#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
                
                # Add the modified player data to the DataFrame
                df_copy = pd.concat([df_copy, new_player_data], ignore_index=True)
                print(f"Added {player_name} to {player_info['Team']}.")
            else:
                print(f"Player {player_name} not found in the DataFrame.")
    
    # Remove duplicates but keep the last occurrence (the new team entry)
    df_copy = df_copy.drop_duplicates(subset=['Player'], keep='last')
    
    return df_copy

    

