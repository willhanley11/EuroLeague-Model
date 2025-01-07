#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def calculate_player_elo_ratings (OffensePlayerDataNEW1,DefensePlayerDataNEW1):

    """
    Calculates player level elo ratings using previously created player possession data.

    Returns player impact ratings for offense/defense eFG%, OReb/DReb, TO, and FTA Rate, as well as pace.
    
    """
    
    # default for k value
    n = 1.5
    
    # k values for each specific stat. the larger the k value, the mroe discrepency there is between very good and very bad at each stat
    k_values = {
        'two_made_for_team': .7,
        'two_missed_for_team': .7,
        'two_fga_for_team': .9,
        'three_made_for_team': .6,
        'three_missed_for_team': .6,
        'three_fga_for_team': .9,
        'fta_for_team': .6,
        'ftm_for_team': .4,
        'oreb_for_team': .6,        
        'to_for_team': .2,
        'Duration': .5,
        'UsagePercent': .5,
        'two_made_against_team': .5,
        'two_missed_against_team': .5,
        'two_fga_against_team': .7,
        'three_made_against_team': .4,
        'three_missed_against_team': .4,
        'three_fga_against_team': .7,
        'fta_against_team': .6,
        'ftm_against_team': .001,
        'oreb_against_team': .6,  
        'to_against_team': .2,
        'UsagePercent': .6}
    
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

