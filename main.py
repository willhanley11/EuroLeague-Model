#!/usr/bin/env python
# coding: utf-8

# In[ ]:

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
from data_collection import get_euroleague_data
from data_cleaning import clean_playbyplay_data
from individual_player_breakdown import individual_player_breakdown
from player_elo_ratings import calculate_player_elo_ratings
from home_court_advantage import home_court_advantage
from transition_matrices import transition_matrix_offense, transition_matrix_defense, calculate_elo_probability, calculate_scaled_pace
from simulation_functions import simulate_possession, calculate_possession_stats, simulate_game, calculate_team_metrics, run_multiple_games, analyze_results, simulate_matchup
from assess_teams import assess_teams, update_or_remove_player_data

def main():
    
    # collect data
    playbyplay, shotdata, boxdata = get_euroleague_data(2022, 2024)

    # clean data    
    cleaned_data = clean_playbyplay_data(playbyplay, boxdata, shotdata)

    # breakdown to player level outcomes and usage    
    OffensePlayerDataNEW1, DefensePlayerDataNEW1, homeusage_for, awayusage_for, homeusage_against, awayusage_against = individual_player_breakdown(cleaned_data,boxdata)

    # elo ratings    
    elo_combined_df = calculate_player_elo_ratings (OffensePlayerDataNEW1,DefensePlayerDataNEW1)
    
    # home court advantage
    homeODiff, homeDDiff, awayODiff, awayDDiff = home_court_advantage(OffensePlayerDataNEW1, DefensePlayerDataNEW1)

    # get current rosters 
    teamsDF = assess_teams(OffensePlayerDataNEW1,elo_combined_df)

    # Simulate game to return team stats and player level box score
    SimmedTeamStats, SimmedBoxScore = run_full_simuluation(
    home_team='MAD', # Madrid
    away_team='BAR', # Barcelona
    HFA=0.8, 
    players_to_update=updated_players, 
    number_of_simulations=15000, 
    possession_adjust=0,
    teamsDF=teamsDF,
    homeusage_for=homeusage_for,
    awayusage_for=awayusage_for,
    homeusage_against=homeusage_against,
    awayusage_against=awayusage_against)




