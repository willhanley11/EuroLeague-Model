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


boxdatabasic = BoxScoreData(competition='E')
boxdatabasic = boxdatabasic.get_player_boxscore_stats_multiple_seasons(2018, 2024)


basicboxscorestats = boxdatabasic[(boxdatabasic['Minutes'] != 'DNP')]

basicboxscorestats['START'] = basicboxscorestats['IsStarter']
basicboxscorestats['PTS'] = basicboxscorestats['Points']


basicboxscorestats['2FGM'] = basicboxscorestats['FieldGoalsMade2']
basicboxscorestats['2FGA'] = basicboxscorestats['FieldGoalsAttempted2']
basicboxscorestats['3FGM'] = basicboxscorestats['FieldGoalsMade3']
basicboxscorestats['3FGA'] = basicboxscorestats['FieldGoalsAttempted3']

basicboxscorestats['FTM'] = basicboxscorestats['FreeThrowsMade']
basicboxscorestats['FTA'] = basicboxscorestats['FreeThrowsAttempted']
basicboxscorestats['ORB'] = basicboxscorestats['OffensiveRebounds']
basicboxscorestats['DRB'] = basicboxscorestats['DefensiveRebounds']

basicboxscorestats['TRB'] = basicboxscorestats['TotalRebounds']
basicboxscorestats['AST'] = basicboxscorestats['Assistances']
basicboxscorestats['TO'] = basicboxscorestats['Turnovers']

basicboxscorestats['BLK'] = basicboxscorestats['BlocksFavour']
basicboxscorestats['BLK_AGAINST'] = basicboxscorestats['BlocksAgainst']
basicboxscorestats['FOUL'] = basicboxscorestats['FoulsCommited']
basicboxscorestats['VALUE'] = basicboxscorestats['Valuation']
basicboxscorestats['PLUSMINUS'] = basicboxscorestats['Plusminus']

basicboxscorestats['STL'] = basicboxscorestats['Steals']
basicboxscorestats['FOUL_RECEIVED'] = basicboxscorestats['FoulsReceived']


def convert_to_seconds(time_str):
    # Handle NaN or empty values
    if pd.isna(time_str) or time_str == '':
        return 0
    
    # Split by colon
    parts = str(time_str).split(':')
    
    # Convert to seconds
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + int(seconds)
    elif len(parts) == 1:
        # In case there's only seconds
        return int(parts[0])
    else:
        # Handle unexpected format
        return 0

# Convert the original string format to total seconds for sorting
basicboxscorestats['Minutes_Seconds'] = basicboxscorestats['Minutes'].apply(convert_to_seconds)

# Create a formatted string for display that maintains sort order
basicboxscorestats['Minutes'] = basicboxscorestats['Minutes_Seconds'].apply(
    lambda x: f"{int(x//60):02d}:{int(x%60):02d}"
)

basicboxscorestats = basicboxscorestats[(basicboxscorestats['Player'] != 'Total') & (basicboxscorestats['Player'] != 'Team')]

basicstats = basicboxscorestats.groupby(by=['Player','Team','Season']).agg({
    'Minutes_Seconds': 'mean',
    'PTS': 'mean',
    'AST': 'mean',
    'ORB': 'mean', 
    'DRB': 'mean',
    'TRB': 'mean',
    'TO': 'mean',
    '2FGM': 'mean',
    '2FGA': 'mean',
    '3FGM': 'mean',
    '3FGA': 'mean',
    'FTM': 'mean',
    'FTA': 'mean',
    'STL': 'mean',
    'BLK': 'mean',
    'BLK_AGAINST': 'mean',
    'FOUL': 'mean',
    'FOUL_RECEIVED': 'mean',
    'VALUE': 'mean',
    'PLUSMINUS': 'mean',
    'Player': 'count',  # This will count the number of rows
    'START': 'sum'    # This will sum the values in the Starter column
}).round(2).sort_values(by='VALUE', ascending=False)

# Rename the count and sum columns
basicstats = basicstats.rename(columns={'Player': 'GP', 'Starter': 'START'})

# Then convert the Minutes_Seconds back to your desired format
basicstats['MINUTES'] = basicstats['Minutes_Seconds'].apply(
    lambda x: f"{int(x//60):02d}:{int(x%60):02d}"
)

# Drop the seconds column if you don't need it
basicstats = basicstats.drop('Minutes_Seconds', axis=1)

basicstats['eFG%'] = (((basicstats['2FGM'] + 1.5 * basicstats['3FGM']) / (basicstats['2FGA'] + basicstats['3FGA']))*100).round(2)
basicstats['AST/TO'] = (basicstats['AST'] / basicstats['TO']).round(2)
basicstats['START'] = basicstats['START'].astype(int)
basicstats['2PT%'] = (((basicstats['2FGM'] / basicstats['2FGA']))*100).round(2)
basicstats['3PT%'] = (((basicstats['3FGM'] / basicstats['3FGA']))*100).round(2)
basicstats['FT%'] = (((basicstats['FTM'] / basicstats['FTA']))*100).round(2)

basicstats['FG%'] = ((((basicstats['2FGM'] + basicstats['3FGM'])/ (basicstats['2FGA'] +basicstats['3FGA'])))*100).round(2)



basicstats = basicstats[['GP', 'START', 'MINUTES', 'PTS', 'TRB', 'AST', 'STL', 'BLK', 'TO', 'FOUL', 
            'FG%', '2FGM', '2FGA', '2PT%', '3FGM', '3FGA', '3PT%', 'FTM', 'FTA', 'FT%',
            'ORB', 'DRB', 'FOUL_RECEIVED', 'BLK_AGAINST', 'AST/TO', 'eFG%', 'VALUE', 'PLUSMINUS']]

basicstats = basicstats.reset_index()

basicstats = basicstats.fillna(0)

# Create a PER40 stats dataset
per40stats = basicstats.copy()

# Define function to convert minutes string to seconds
def minutes_to_seconds(min_str):
    try:
        parts = min_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return 0

# Calculate the minutes played as a fraction of 40 minutes (2400 seconds)
per40stats['Minutes_Seconds'] = per40stats['MINUTES'].apply(minutes_to_seconds)
per40stats['MINUTES_FRACTION'] = per40stats['Minutes_Seconds'] / 2400

# List of all counting stats that should be normalized 
counting_stats = ['PTS', 'TRB', 'AST', 'STL', 'BLK', 'TO', 'FOUL', 
                 '2FGM', '2FGA', '3FGM', '3FGA', 'FTM', 'FTA',
                 'ORB', 'DRB', 'FOUL_RECEIVED', 'BLK_AGAINST']

# Normalize each counting stat to PER40
for stat in counting_stats:
    if stat in per40stats.columns:
        per40stats[stat] = (per40stats[stat] / per40stats['MINUTES_FRACTION']).round(2)

# Recalculate the percentages based on the new normalized attempts and makes
per40stats['FG%'] = ((((per40stats['2FGM'] + per40stats['3FGM'])/ (per40stats['2FGA'] + per40stats['3FGA'])))*100).round(2)
per40stats['2PT%'] = (((per40stats['2FGM'] / per40stats['2FGA']))*100).round(2)
per40stats['3PT%'] = (((per40stats['3FGM'] / per40stats['3FGA']))*100).round(2)
per40stats['FT%'] = (((per40stats['FTM'] / per40stats['FTA']))*100).round(2)
per40stats['eFG%'] = (((per40stats['2FGM'] + 1.5 * per40stats['3FGM']) / (per40stats['2FGA'] + per40stats['3FGA']))*100).round(2)
per40stats['AST/TO'] = (per40stats['AST'] / per40stats['TO']).round(2)

# VALUE and PLUSMINUS should be normalized too
per40stats['VALUE'] = (per40stats['VALUE'] / per40stats['MINUTES_FRACTION']).round(2)
per40stats['PLUSMINUS'] = (per40stats['PLUSMINUS'] / per40stats['MINUTES_FRACTION']).round(2)

# Drop the temporary columns used for calculation
per40stats = per40stats.drop(['Minutes_Seconds', 'MINUTES_FRACTION'], axis=1)

# Fill any NaN values that might result from division by zero
per40stats = per40stats.fillna(0)


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Save basicstats as pickle file
basicstats_path = os.path.join(script_dir, 'BasicStats.pkl')
with open(basicstats_path, 'wb') as f:
    pickle.dump(basicstats, f)
print(f"Basic stats saved to {basicstats_path}")

# Save per40stats as pickle file
per40stats_path = os.path.join(script_dir, 'Per40Stats.pkl')
with open(per40stats_path, 'wb') as f:
    pickle.dump(per40stats, f)
print(f"Per40 stats saved to {per40stats_path}")