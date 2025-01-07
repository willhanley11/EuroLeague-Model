#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
def analyze_results(results, simmedpossessions, team_a_name, team_b_name):
    filtered_results = [game for game in results if game[0]['Points'] != game[1]['Points']]

    team_a_totals = {key: sum(game[0][key] for game in filtered_results) for key in results[0][0]}
    team_b_totals = {key: sum(game[1][key] for game in filtered_results) for key in results[0][1]}
    
    num_games = len(filtered_results)  # Update number of games to only include non-tied games

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
        
        metrics_data.append({"Metric": "Win Percentage", team_a_name: team_a_wins / num_games, team_b_name: team_b_wins / num_games})

        total_team_a_points = sum(game[0]['Points'] for game in filtered_results)
        total_team_b_points = sum(game[1]['Points'] for game in filtered_results)
        
        sup_team_a = (total_team_a_points - total_team_b_points)/num_games
        sup_team_b = (total_team_b_points - total_team_a_points)/num_games
        
        metrics_data.append({"Metric": "Supremacy", team_a_name: sup_team_a, team_b_name: sup_team_b})

        total_points = (total_team_a_points + total_team_b_points)/num_games
        metrics_data.append({"Metric": "Total", team_a_name: total_points, team_b_name: total_points})
        metrics_data.append({"Metric": "Possessions", team_a_name: simmedpossessions, team_b_name: simmedpossessions})

    results_df = pd.DataFrame(metrics_data)

    return results_df

def simulate_matchup(home_team,away_team,HFA, number_of_simulations, possessionAdjust):
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