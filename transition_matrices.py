#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Function which uses Elo ratings to create scaled probabilities
def calculate_elo_probability(rating, target_prob, target_rating=1500, scale_factor=1000):
    base_rating = target_rating + scale_factor * math.log10((1 / target_prob) - 1)
    exponent = (rating - base_rating) / scale_factor
    return 1 / (1 + math.pow(10, -exponent))

    
# Function which uses Elo ratings to create pace target number
def calculate_scaled_pace(pace_O, pace_D, target_value=70.1, reference_rating=1500):
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
        ft_attempt_prob = calculate_elo_probability(team_ratings['fta_O'], target_prob=0.09)
        two_point_attempt_prob = calculate_elo_probability(team_ratings['two_attempt_O'], target_prob=0.41)
        three_point_attempt_prob = calculate_elo_probability(team_ratings['three_attempt_O'], target_prob=0.28)
    
        three_made_prob = calculate_elo_probability(team_ratings['three_made_O'], target_prob=0.37)
        two_made_prob = calculate_elo_probability(team_ratings['two_made_O'], target_prob=0.55)
        ft_made_prob = calculate_elo_probability(team_ratings['ftm_O'], target_prob=0.78)

        ft_oreb_prob = calculate_elo_probability(team_ratings['oreb_O'], target_prob=0.175)
        two_pt_oreb_prob = calculate_elo_probability(team_ratings['oreb_O'], target_prob=0.327)
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

