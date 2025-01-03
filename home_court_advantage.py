#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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

