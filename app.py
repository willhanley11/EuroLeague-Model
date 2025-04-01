import streamlit as st
import pandas as pd
import os
import pickle


def create_sample_data_euroleague(simulation_data=None):
    """
    Create sample data frames from simulation results.
    
    Parameters:
    simulation_data (DataFrame, optional): Simulation results data to process.
                                          If None, loads Round 29 data by default.
    
    Returns:
    tuple: (team_stats_df, box_scores_team1_df, box_scores_team2_df)
    """
    # If no data provided, load default (Round 29) data
    if simulation_data is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pickle_path = os.path.join(script_dir, 'data', 'euroleague_simulations_round_33.pkl')
        
        with open(pickle_path, 'rb') as f:
            simulation_data = pickle.load(f)
    
    team_stats_list = []
    box_scores_team1_list = []  # Will store home team data
    box_scores_team2_list = []  # Will store away team data
    
    for _, row in simulation_data.iterrows():
        matchup = row['Matchup']
        home_code = row['Home_Code']
        away_code = row['Away_Code']
        
        # Process team stats
        for metric, value in row['SimmedTeamStats'].items():
            team_stats_list.append({'Matchup': matchup, 'Team': home_code, 'Metric': metric, 'Value': value})
        
        # Correctly assign box scores
        team1_box = row['SimmedBoxScoreTeam1'].copy()  # Home team players
        team2_box = row['SimmedBoxScoreTeam2'].copy()  # Away team players
        
        team1_box['Matchup'] = matchup
        team2_box['Matchup'] = matchup
        
        box_scores_team1_list.append(team1_box)
        box_scores_team2_list.append(team2_box)
    
    # Convert lists to DataFrames
    team_stats_df = pd.DataFrame(team_stats_list)
    box_scores_team1_df = pd.concat(box_scores_team1_list, ignore_index=True).sort_values(by='PTS', ascending=False)
    box_scores_team2_df = pd.concat(box_scores_team2_list, ignore_index=True).sort_values(by='PTS', ascending=False)
    
    return team_stats_df, box_scores_team1_df, box_scores_team2_df

def create_sample_data_eurocup():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pickle_path = os.path.join(script_dir, 'data', 'eurocup_simulations_semifinals_game_3.pkl')
    
    with open(pickle_path, 'rb') as f:
        simulation_results_df = pickle.load(f)
    
    team_stats_list = []
    box_scores_team1_list = []  # Will store home team data
    box_scores_team2_list = []  # Will store away team data
    
    for _, row in simulation_results_df.iterrows():
        matchup = row['Matchup']
        home_code = row['Home_Code']
        away_code = row['Away_Code']
        
        # Process team stats
        for metric, value in row['SimmedTeamStats'].items():
            team_stats_list.append({'Matchup': matchup, 'Team': home_code, 'Metric': metric, 'Value': value})
        
        # Correctly assign box scores
        team1_box = row['SimmedBoxScoreTeam1'].copy()  # Home team players
        team2_box = row['SimmedBoxScoreTeam2'].copy()  # Away team players
        
        team1_box['Matchup'] = matchup
        team2_box['Matchup'] = matchup
        
        box_scores_team1_list.append(team1_box)
        box_scores_team2_list.append(team2_box)
    
    # Convert lists to DataFrames
    team_stats_df = pd.DataFrame(team_stats_list)
    box_scores_team1_df = pd.concat(box_scores_team1_list, ignore_index=True).sort_values(by='PTS', ascending=False)
    box_scores_team2_df = pd.concat(box_scores_team2_list, ignore_index=True).sort_values(by='PTS', ascending=False)
    
    return team_stats_df, box_scores_team1_df, box_scores_team2_df




























def render_stats_tables_euroleague(selected_matchup, matchups, table_key_prefix=""):
   simulation_results_df = st.session_state.get('simulation_results_df')
   if simulation_results_df is None:
       st.error("Unable to load simulation results")
       return
   
   matchup_data = simulation_results_df[simulation_results_df['Matchup'] == selected_matchup].iloc[0]
   home_logo = matchup_data['Home_Logo']
   away_logo = matchup_data['Away_Logo']
   home_team = matchup_data['Home_Team']
   away_team = matchup_data['Away_Team']
   home_code2 = matchup_data['Home_Code']
   away_code2 = matchup_data['Away_Code']
   
   # Define team colors dictionary 
   euroleague_team_colors = {
  'BER': '#ffe14d',  # ALBA Berlin - Softer yellow
  'IST': '#3379bd',  # Anadolu Efes - Softer royal blue
  'MCO': '#d44150',  # Monaco - Softer red
  'BAS': '#3773b3',  # Baskonia - Softer navy blue
  'RED': '#e75a6b',  # Crvena Zvezda - Softer red
  'MIL': '#ff5e75',  # Milan - Softer red with pink tone
  'BAR': '#3674b5',  # Barcelona - Softer deep blue
  'MUN': '#c54960',  # Bayern - Softer burgundy
  'ULK': '#ffd54d',  # Fenerbahce - Softer golden yellow
  'ASV': '#a3a6a9',  # ASVEL - Softer gray
  'TEL': '#ffc966',  # Maccabi - Softer golden orange
  'OLY': '#e66464',  # Olympiacos - Softer red
  'PAN': '#338855',  # Panathinaikos - Softer dark green
  'PRS': '#5d6772',  # Paris - Softer slate
  'PAR': '#4f4d48',  # Partizan - Softer black-gray
  'MAD': '#c0c0c0',  # Real Madrid - Silver instead of white
  'VIR': '#454545',  # Virtus - Softer black
  'ZAL': '#339966',  # Zalgiris - Softer kelly green
}
   euroleague_team_colors_light = {
    'BER': '#ffe99e',  # ALBA Berlin - Darker light yellow
    'IST': '#b0c9f0',  # Anadolu Efes - Darker light blue
    'BAS': '#a0bfed',  # Baskonia - Darker light navy blue
    'MCO': '#f0b7bd',  # Monaco - Darker light red
    'RED': '#f2b6bf',  # Crvena Zvezda - Darker light red
    'MIL': '#ffb5c2',  # Milan - Darker light pink-red
    'BAR': '#a0bfed',  # Barcelona - Darker light deep blue
    'MUN': '#e5adb9',  # Bayern - Darker light burgundy
    'ULK': '#ffe69e',  # Fenerbahce - Darker light golden yellow
    'ASV': '#c7c9cc',  # ASVEL - Darker light gray
    'TEL': '#ffd699',  # Maccabi - Darker light golden orange
    'OLY': '#f2b6b6',  # Olympiacos - Darker light red
    'PAN': '#a0d4b6',  # Panathinaikos - Darker light green
    'PRS': '#b5bac2',  # Paris - Darker light slate
    'PAR': '#b8b6b2',  # Partizan - Darker light gray
    'MAD': '#d9d9d9',  # Real Madrid - Darker light silver
    'VIR': '#b3b3b3',  # Virtus - Darker light black-gray
    'ZAL': '#9ad9bc',  # Zalgiris - Darker light kelly green
}
   team_name_short = {
   'BER': 'ALBA BERLIN',
   'IST': 'ANADOLU EFES',
   'MCO': 'AS MONACO', 
   'BAS': 'BASKONIA',
   'RED': 'CRVENA ZVEZDA',
   'MIL': 'OLIMPIA MILANO',
   'BAR': 'FC BARCELONA',
   'MUN': 'BAYERN MUNICH',
   'ULK': 'FENERBAHCE',
   'ASV': 'LDLC ASVEL',
   'TEL': 'MACCABI TEL AVIV',
   'OLY': 'OLYMPIACOS',
   'PAN': 'PANATHINAIKOS',
   'PRS': 'PARIS BASKETBALL',
   'PAR': 'PARTIZAN MOZZART',
   'MAD': 'REAL MADRID',
   'VIR': 'VIRTUS BOLOGNA',
   'ZAL': 'ZALGIRIS KAUNAS',
}

   
   team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_euroleague(simulation_results_df)
   filtered_team_stats = team_stats[team_stats['Matchup'] == selected_matchup]
   filtered_player_statsTeam1 = player_statsTeam1[player_statsTeam1['Matchup'] == selected_matchup]
   filtered_player_statsTeam2 = player_statsTeam2[player_statsTeam2['Matchup'] == selected_matchup]
   filtered_player_statsTeam1 = player_statsTeam1[player_statsTeam1['Matchup'] == selected_matchup].copy()
   filtered_player_statsTeam2 = player_statsTeam2[player_statsTeam2['Matchup'] == selected_matchup].copy()

# Rename the column in both DataFrames
   filtered_player_statsTeam1 = filtered_player_statsTeam1.rename(columns={'3FGM': '3FG', '2FGM': '2FG', 'FTM':'FT'})
   filtered_player_statsTeam2 = filtered_player_statsTeam2.rename(columns={'3FGM': '3FG', '2FGM': '2FG', 'FTM':'FT'})

   # Add state management for HCA and possessions
   if 'hca' not in st.session_state:
       st.session_state.hca = 80
   if 'possessions' not in st.session_state:
       st.session_state.possessions = 72
   
   st.markdown("""
       <style>
       .table-container {
           border: 3px !important;;
           border-radius: 16px;
           background-color: white;
           margin: -5px -10px 10px -10px;
           box-shadow: 0 0 0 1px rgba(0,0,0,0.08);

       }

       .logo-cell {
           display: flex;
           flex-direction: column;
           align-items: center;
           justify-content: center;
           padding: 10px;
           background-color: white;
           border-radius: 8px;
           box-shadow: 0 4px 20px rgba(100, 100, 100, 3.5);
           margin-bottom: 8px;
           margin-top: -15px !important;
       }

       .logo-cell img {
           width: 200px;
           height: 200px;
           object-fit: contain;
       }

       .team-name-box {
           background-color: white;
           border-radius: 8px;
           padding: 8px;
           box-shadow: 0 4px 10px rgba(100, 100, 100, 1.5);
           margin-bottom: 6px;
           width: 100%;
           text-align: center;
       }

       .team-name {
           font-weight: 700;
           font-size: 11px !important;
           font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
           color: rgba(26, 31, 54, 0.9);
           white-space: nowrap;
           overflow: hidden;
           text-overflow: ellipsis;
       }
.team-stats-euroleague-container {
    background-color: white;
    border-radius: 16px;
    color: rgb(26, 31, 54) !important;
    box-shadow: 0 4px 12px rgba(100, 100, 100, .5);
    margin-top: -50px !important;
    margin-left: -60px !important;
    border: 2px solid white !important; 
    overflow: hidden;
    text-align: center;
    border:none;
    border-collapse: collapse;
    border-radius: 16px;
    overflow: hidden;
}

.team-stats-euroleague-table {
    width: 100%;
    border-collapse: collapse;
    border-spacing: 0;
    box-shadow: 0 0 15px rgba(100, 100, 100, 1);
}

/* Enhanced Table header styles */
.team-stats-euroleague-container th {
    color: rgb(26, 31, 54) !important; 
    font-weight: 800;
    font-size: 14px;
    padding: 6px 4px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    position: relative;
    z-index: 1;
}

/* Add hover effect for rows */
.team-stats-euroleague-container tr:hover {
    background: linear-gradient(145deg, #f8f9fa, #f1f3f5) !important;
    transition: background 0.2s ease-in-out !important;
}

/* Preserve background for header row */
.team-stats-euroleague-container thead tr:hover {
    background: none !important;
}

/* Add darker borders for specific rows */
.team-stats-euroleague-container tr:nth-child(1) {
    border-top: 8px solid #e0e0e0 !important;
}

.team-stats-euroleague-container tr:nth-child(2) {
    border-top: 8px solid #e0e0e0;
}

.team-stats-euroleague-container tr:nth-child(6) {
    border-top: 8px solid #e0e0e0;
}

.team-stats-euroleague-container tr:nth-child(9) {
    border-top: 8px solid #e0e0e0;
}

/* Add a subtle line between header cells */
.team-stats-euroleague-container th:not(:last-child) {
    border-right: 1px solid #e0e0e0;
}
/* Highlighting styles */
.highlight {
    background-color: #fff4b3;
    position: relative;
    font-weight: 900;
}

.team-name {
    font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    font-weight: 800;
    font-size: 12px;
    color: #1a1f36;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-transform: uppercase;
    letter-spacing: 0.1px;
}


       </style>
   """, unsafe_allow_html=True)

   
   first_row = simulation_results_df[simulation_results_df['Matchup'] == selected_matchup].iloc[0]
   st.markdown('<div class="euroleague_tab">', unsafe_allow_html=True)

   team_stats_area, spacing1, logo_area,  stats_area = st.columns([1.4, 0.9, 4,  2.6])
   
   with team_stats_area:
       # Team Stats Table (Full Width)
       team_stats_df = pd.DataFrame(first_row['SimmedTeamStats']).T
       # Reset the index to make the current index a column
       team_stats_df = team_stats_df.reset_index()
       # Set the first row as the new column names
       team_stats_df.columns = team_stats_df.iloc[0]
       # Drop the first row (since it's now the column names)
       team_stats_df = team_stats_df.drop(0).reset_index(drop=True) 
       team_stats_df['PTS'] = team_stats_df['Points']
       team_stats_df['3ptA'] = team_stats_df['3pt Attempts']
       team_stats_df['3ptM'] = team_stats_df['3pt Makes']
       team_stats_df['2ptA'] = team_stats_df['2pt Attempts']
       team_stats_df['2ptM'] = team_stats_df['2pt Makes']
       team_stats_df['FTA'] = team_stats_df['FT Attempts']
       team_stats_df['FTM'] = team_stats_df['FT Makes']
       team_stats_df['TO'] = team_stats_df['Turnovers']
       team_stats_df['FTA%'] = team_stats_df['FTA%'] * 100
       team_stats_df['OREB%'] = team_stats_df['OR%'] *100
       team_stats_df['2pt%'] = team_stats_df['2pt%'] * 100
       team_stats_df['3pt%'] = team_stats_df['3pt%'] *100
       team_stats_df['FT%'] = team_stats_df['FT%'] *100
       team_stats_df['TO%'] = team_stats_df['Turnovers']/team_stats_df['Possessions'] *100
       team_stats_df['eFG%'] = (team_stats_df['2ptM'] + 1.5* team_stats_df['3ptM'])/(team_stats_df['2ptA'] + team_stats_df['3ptA']) *100
       team_stats_df = team_stats_df.rename(columns={'Metric': 'Team'})
       team_stats_df = team_stats_df[['Team','PTS','eFG%','TO%','OREB%','FTA%','3pt%', '2pt%','FT%','3ptM','3ptA','2ptM','2ptA','FTM','FTA']]

       # When doing the final transpose, keep the index
       team_stats_df = team_stats_df.set_index('Team').T.reset_index()
       team_stats_df = team_stats_df.rename(columns={0: ''})
       cols = team_stats_df.columns.tolist()
       cols[1], cols[2] = cols[2], cols[1]  # Swap the columns
       team_stats_df = team_stats_df[cols]
       # Convert team colors to RGB format for CSS variables
       

       # Convert team colors to RGB format for CSS variables
       home_code = home_code2
       away_code = away_code2

    # Explicitly create RGB values using EuroCup team colors
       local_team_colors = dict(euroleague_team_colors)

    # Use local_team_colors instead of euroleague_team_colors
       away_team_color = local_team_colors.get(away_code2, '#f0f0f0')
       home_team_color = local_team_colors.get(home_code2, '#f0f0f0')

    # Create the CSS variables
       team_css = f"""
    <style>
        .team-stats-euroleague-container th:nth-child(1) {{
            background: linear-gradient(to bottom, 
        rgb(255, 255, 255), 
        rgb(245, 245, 247);
        }}

        .team-stats-euroleague-container th:nth-child(2) {{
            background: linear-gradient(to bottom, 
                rgba(255, 255, 255, 0.7),
                {away_team_color}
            ) !important;
        }}

        .team-stats-euroleague-container th:nth-child(3) {{
            background: linear-gradient(to bottom,
                rgba(255, 255, 255, 0.7),
                {home_team_color}
            ) !important;
        }}
       </style>
       """

       # Apply the CSS
       st.markdown(team_css, unsafe_allow_html=True)
       # Convert team colors to RGB format for CSS variables
       team_html = """
       <div class="team-stats-euroleague-container">
           <table style="width: 100%">
               <colgroup>
                   <col style="width: 8%">
                   <col style="width: 46%">
                   <col style="width: 46%">
               </colgroup>
               <thead><tr>{}</tr></thead>
               <tbody>{}</tbody>
           </table>
       </div>
       """

       
       team_header = f"""<th>{team_stats_df.columns[0]}</th>
<th>
   <div style="display: flex; align-items: center; gap: 2px; justify-content: center;">
       <div style="width: 40px; height: 40px; display: flex; align-items: center; padding: 2px;">
           <img src="{away_logo}" alt="Logo" style="width: 100%; height: 650px; object-fit: contain;">
       </div>
       <span>{team_stats_df.columns[1]}</span>
   </div>
</th>
<th>
   <div style="display: flex; align-items: center; gap: 2px; justify-content: center;">
       <div style="width: 40px; height: 40px; display: flex; align-items: center; padding: 2px;">
           <img src="{home_logo}" alt="Logo" style="width: 100%; height: 650px; object-fit: contain;">
       </div>
       <span>{team_stats_df.columns[2]}</span>
   </div>
</th>"""

       # CSS for highlighting
       highlight_css = """
       <style>
           .highlight {
               position: relative;
               font-weight: 900;
           }
       </style>
       """

       # Add the CSS to the Streamlit app
       st.markdown(highlight_css, unsafe_allow_html=True)

       # Generate the table rows with conditional highlighting
       team_rows = ''.join(
    f'<tr class="{" ".join(filter(None, [
        "first-row" if index == 0 else "",
        "section-start" if index == 1 else "",
        "key-section" if 1 <= index <= 4 else ""
    ]))}">' +
    ''.join(
        f'<td class="numeric" style="text-align: center; font-weight: 1000; font-size: 12px;">{value}</td>' 
        if idx == 0
        else f'<td class="numeric" style="text-align: center"><div style="margin-left: -2px;font-size: 12px;margin-right:-5px;"><span class="highlight" style="padding: 3px 3px; border-radius: 4px; background-color: {euroleague_team_colors_light[team_stats_df.columns[1]] if (idx == 1 and ((value > row[2] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[2] and row.iloc[0] in ["TO%", "TO"]))) else "transparent"}">{f"{value:.1f}%" if str(row.iloc[0]).endswith("%") else f"&nbsp;{value:>5.1f}&nbsp;"}</span>{f"<img src=\'{away_logo}\' style=\'width: 25px; height: 25px; margin-left: 2px; vertical-align: middle;\'/>" if (idx == 1 and ((value > row[2] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[2] and row.iloc[0] in ["TO%", "TO"]))) else ""}</div></td>' 
        if isinstance(value, (int, float)) and idx == 1
        else f'<td class="numeric" style="text-align: center"><div style="margin-left: -2px;font-size: 12px;margin-right:-5px;"><span class="highlight" style="padding: 3px 3px; border-radius: 4px; background-color: {euroleague_team_colors_light[team_stats_df.columns[2]] if (idx == 2 and ((value > row[1] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[1] and row.iloc[0] in ["TO%", "TO"]))) else "transparent"}">{f"{value:.1f}%" if str(row.iloc[0]).endswith("%") else f"&nbsp;{value:>5.1f}&nbsp;"}</span>{f"<img src=\'{home_logo}\' style=\'width: 25px; height: 25px; margin-left: 2px; vertical-align: middle;\'/>" if (idx == 2 and ((value > row[1] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[1] and row.iloc[0] in ["TO%", "TO"]))) else ""}</div></td>' 
        if isinstance(value, (int, float)) and idx == 2
        else f'<td style="text-align: center">{value}</td>'
        for idx, (col, value) in enumerate(row.items())
    ) + 
    '</tr>'
    for index, row in team_stats_df.iterrows()
)

       # Render the table
       st.markdown(team_html.format(team_header, team_rows), unsafe_allow_html=True)
   
       with logo_area:
          away_logo_col, vs_col, home_logo_col, = st.columns([1, 0.2, 1])
          
          with away_logo_col:
              st.markdown(
                  f"""
                  <div class="logo-cell" style="background-color: {euroleague_team_colors[away_code2]}">
                      <img src="{away_logo}" alt="{away_team} Logo">
                  </div>
                  <div class="team-name-box">
                      <div class="team-name">{team_name_short[away_code2]}</div>
                  </div>
                  """,
                  unsafe_allow_html=True
              )
          
          with vs_col:
              st.markdown("""
              <div style='display: flex; justify-content: center; align-items: center;'>
                  <div style='background-color: white; 
                            border-radius: 8px; 
                            padding: 3px 8px; 
                            box-shadow: 0 4px 12px rgba(100, 100, 100, .4);
                            margin-top: 45px;'>
                      <span style='font-size: 16px; color: #1a1f36; font-weight: 800;'>@</span>
                  </div>
              </div>
              """, unsafe_allow_html=True)
          
          with home_logo_col:
              st.markdown(
                  f"""
                  <div class="logo-cell" style="background-color: {euroleague_team_colors[home_code2]}">
                      <img src="{home_logo}" alt="{home_team} Logo">
                  </div>
                  <div class="team-name-box">
                      <div class="team-name">{team_name_short[home_code2]}</div>
                  </div>
                  """,
                  unsafe_allow_html=True
              )


   with stats_area:
       first_row = simulation_results_df[simulation_results_df['Matchup'] == selected_matchup].iloc[0]
       summary_stats_df = pd.DataFrame(first_row['SimmedTeamStats'][-3:]).T
       
       summary_stats_df.columns = summary_stats_df.iloc[0]
       summary_stats_df = summary_stats_df.drop(summary_stats_df.index[0])
       summary_stats_df = summary_stats_df.rename(columns={'Total Adjusted': 'Total'})
       summary_stats_df = summary_stats_df[['Spread', 'Total', 'Money']]
       
       html_table = """
       <div class="summary-stats-euroleague">  <!-- or summary-stats-eurocup -->
           <table width="100%">
               <thead>
                   <tr>
                       <th>Team</th>
"""
       for col in summary_stats_df.columns:
           html_table += f"<th>{col}</th>"
       
       html_table += """
                   </tr>
               </thead>
               <tbody>
       """
       
       for idx, row in summary_stats_df.iterrows():
           html_table += "<tr>"

           logo_to_use = home_logo if idx == summary_stats_df.index[0] else away_logo
           team_name = home_code2 if idx == summary_stats_df.index[0] else away_code2

           html_table += f'''
               <td>
                   <div style="display: flex; align-items: center; justify-content: center; gap: 6px; padding: 5px; margin-left:0px;">
                       <div style="width: 30px; height: 30px; display: flex; align-items: center;">
                           <img src="{logo_to_use}" alt="Logo" style="width: 100%; height: auto; object-fit: contain;margin-left:0px;">
                       </div>
                       <span style="font-size: 14px; font-weight: 800; color: rgba(0,0,0,0.7);">{team_name}</span>
                   </div>
               </td>
           '''

           for col, val in row.items():
               if isinstance(val, (int, float)):
                   if val > 1:
                       style_class = "metric-high"
                   elif val > 1:
                       style_class = "metric-medium"
                   else:
                       style_class = "metric-low"

                   if col == "Money":
                       html_table += f'<td class="{style_class}">{val:.2f}</td>'
                   else:
                       html_table += f'<td class="{style_class}">{val:.1f}</td>'
               else:
                   html_table += f"<td>{val}</td>"
           html_table += "</tr>"

       html_table += """
               </tbody>
           </table>
       </div>
       """

       st.markdown(html_table, unsafe_allow_html=True)
   st.markdown("<div style='margin: 0px 0;'></div>", unsafe_allow_html=True)


 
# Create a second row of columns for player stats table
  # Create a second row of columns for player stats table
   # Create a second row of columns for player stats table
   # Create a second row of columns for player stats table
   _, select_col, _ = st.columns([.001, .001, .001])  
  
   with select_col:
      # Get team names from matchup data
      first_row = simulation_results_df[simulation_results_df['Matchup'] == selected_matchup].iloc[0]
      away_team = first_row['Away_Code']
      home_team = first_row['Home_Code']
      
      # Unified CSS block
      st.markdown("""
          <style>
          /* Button Styles */
          /* Button container styling */
div.stButton {
   margin-top: -480px !important;
   margin-left: -50px !important;  /* This moves buttons up */
   position: relative !important;
   z-index: 2 !important;  /* Ensure buttons stay on top */
   padding: 0 !important;  /* Remove padding */
   margin-bottom: -8px !important;  /* Reduce space between buttons */
}

/* Individual button styling */
div.stButton > button {
   width: 100%;
   background-color: #1a1f36;
   border: 3px solid #1a1f36;  /* Reduced border from 5px to 2px */
   color: white;
   font-weight: 700;
   border-radius: 8px;
   font-size: 6px !important;
   padding: 3px 3px !important;  /* Reduced padding */
   min-height: 20px !important;  /* Reduced height */
   height: 20px !important;  /* Set explicit height */
   line-height: 20px !important;  /* Match line height to height */
}

div.stButton > button:hover {
   border-color: #2d63e2;
   color: #2d63e2;
   background-color: rgba(45, 99, 226, 0.1);
}

div.stButton > button:focus {
   box-shadow: none;
   background-color: rgba(45, 99, 226, 0.1);
   color: #2d63e2;
   border-color: #2d63e2;
}

/* Base Table Styles */
.player-stats-container {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 0 15px rgba(100, 100, 100, .5);
}

.player-stats-table {
    font-size: 11px !important;


    border-spacing: 0 !important;  /* Added to ensure consistent spacing */
    border-collapse: collapse !important;  /* Added to ensure consistent spacing */
}

/* Increased heights for headers */
.player-stats-table th {
    font-weight: 700 !important;
    color: rgb(26, 31, 54); /* Consistent dark text color */
    background-color: rgb(255, 255, 255) !important;
    font-size: 12px !important;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    height: 20px !important;  /* Increased from 30px */
    line-height: 5px !important;  /* Added to match height */
    vertical-align: middle !important;
}

/* Increased heights for cells */
.player-stats-table td {
    padding: 8px 4px !important;  /* Increased top/bottom padding */
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    height: 35px !important;  /* Increased from 25px */
    line-height: 15px !important;  /* Added to match height */
    vertical-align: middle !important;
}

/* Add some subtle borders for better readability */
.player-stats-table tr {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
}

/* All View Table Styles */
.all-view.player-stats-container {
    min-width: 310px !important;
    width: 310px !important;
    max-width: 310px !important;
    overflow: hidden !important;  /* Prevent scrolling in All view */
}

.all-view.player-stats-container.left-table {
    position: relative !important;
    left: 30px !important;
}

.all-view.player-stats-container.right-table {
    position: relative !important;
    margin-left: 0px !important;
}

.all-view .player-stats-table td:first-child,
.all-view .player-stats-table th:first-child {
    width: 120px !important;
    background: rgb(255, 255, 255) !important;  /* Pure white background */
    border-right: 1px solid rgba(200, 200, 200, 0.4) !important;  /* Slightly more visible separator */
    box-shadow: 1px 0 2px rgba(0, 0, 0, 0.05) !important;  /* Subtle shadow for depth */
}

/* Also ensure the text remains clearly visible */
.player-stats-table td:first-child {
    color: #1a1f36 !important;  /* Darker text color for better contrast */
    font-weight: 700 !important;
}

/* Add hover effect for more metallic feel */
.all-view .player-stats-table td:first-child:hover {
    background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important;
}



/* Individual Team View Styles */
.player-stats-container.single-team {
    min-width: 1020px !important;
    width: 1020px !important;
    max-width: 1020px !important;
    margin-right: 0px !important;
    overflow-x: scroll !important;
}

/* Individual view specific column widths */
.single-team .player-stats-table {
    min-width: 800px !important; /* Make table wider than container to enable scroll */
    table-layout: fixed !important;
}

.single-team .player-stats-table td:first-child,
.single-team .player-stats-table th:first-child {
    width: 140px !important;
    text-align: left !important;
    padding-left: 8px !important;
    position: sticky !important;
    left: 0 !important;
    background: white !important;
    z-index: 1 !important;
}

/* More specific selector with increased specificity */
.single-team.player-stats-container .player-stats-table td:not(:first-child),
.single-team.player-stats-container .player-stats-table th:not(:first-child) {
    width: 57px !important;
    min-width: 57px !important;
    max-width: 57px !important;
    flex: 0 0 57px !important;
}


/* Custom scrollbar for individual team view */
.player-stats-container.single-team::-webkit-scrollbar {
    height: 8px !important;
}

.player-stats-container.single-team::-webkit-scrollbar-track {
    background: #f1f1f1 !important;
    border-radius: 4px !important;
}

.player-stats-container.single-team::-webkit-scrollbar-thumb {
    background: #888 !important;
    border-radius: 4px !important;
}

.player-stats-container.single-team::-webkit-scrollbar-thumb:hover {
    background: #555 !important;
}
          </style>
      """, unsafe_allow_html=True)
      
      # Create three columns for the buttons
      btn1, btn3, btn2 = st.columns([0.01, 0.01, 0.01])
      
      # Initialize session state for button selection
      if 'selected_view' not in st.session_state:
          st.session_state.selected_view = 'All'
      
      with btn1:
          if st.button('All', key=f'game_view_btn_{table_key_prefix}'):
              st.session_state.selected_view = 'All'
      with btn2:
          if st.button(home_team, key=f'home_team_btn_{table_key_prefix}'):
              st.session_state.selected_view = 'Home'
      with btn3:
          if st.button(away_team, key=f'away_team_btn_{table_key_prefix}'):
              st.session_state.selected_view = 'Away'
      view_options = {
          'All': 'All',
          'Home': 'team1',
          'Away': 'team2'
      }
      
      selected_view = st.session_state.selected_view

   def create_player_stats_html(df, display_columns, team_code):
      # Create color shades dictionary based on team base colors
      team_color_shades = {
          # Yellow shades (based on #ffed99)
          'BER': ['#ffd966', '#ffe180', '#ffed99', '#fff4cc', '#fff7e0', '#fff9e6'],
          'ULK': ['#ffd966', '#ffe180', '#ffed99', '#fff4cc', '#fff7e0', '#fff9e6'],
          'TEL': ['#ffd966', '#ffe180', '#ffed99', '#fff4cc', '#fff7e0', '#fff9e6'],
          
          # Light navy/blue shades (based on #d6e4ff)
          'IST': ['#adc8ff', '#c2d6ff', '#d6e4ff', '#e4edff', '#edf3ff', '#f2f5ff'],
          'BAS': ['#adc8ff', '#c2d6ff', '#d6e4ff', '#e4edff', '#edf3ff', '#f2f5ff'],
          'BAR': ['#adc8ff', '#c2d6ff', '#d6e4ff', '#e4edff', '#edf3ff', '#f2f5ff'],
          'MAD': ['#adc8ff', '#c2d6ff', '#d6e4ff', '#e4edff', '#edf3ff', '#f2f5ff'],
          
          # Light red shades (based on #ffd6d9)
          'MCO': ['#ffb3b9', '#ffc4c9', '#ffd6d9', '#ffe4e6', '#ffeff0', '#fff2f3'],
          'RED': ['#ffb3b9', '#ffc4c9', '#ffd6d9', '#ffe4e6', '#ffeff0', '#fff2f3'],
          'MIL': ['#ffb3b9', '#ffc4c9', '#ffd6d9', '#ffe4e6', '#ffeff0', '#fff2f3'],
          'MUN': ['#ffb3b9', '#ffc4c9', '#ffd6d9', '#ffe4e6', '#ffeff0', '#fff2f3'],
          'OLY': ['#ffb3b9', '#ffc4c9', '#ffd6d9', '#ffe4e6', '#ffeff0', '#fff2f3'],
          
          # Light green shades (based on #d6ffe0)
          'PAN': ['#adffbd', '#c2ffd1', '#d6ffe0', '#e4ffe9', '#edfff1', '#f2fff5'],
          'ZAL': ['#adffbd', '#c2ffd1', '#d6ffe0', '#e4ffe9', '#edfff1', '#f2fff5'],
          
          # Light gray shades (based on #e6e6e6)
          'ASV': ['#cccccc', '#d9d9d9', '#e6e6e6', '#efefef', '#f3f3f3', '#f7f7f7'],
          'PRS': ['#cccccc', '#d9d9d9', '#e6e6e6', '#efefef', '#f3f3f3', '#f7f7f7'],
          'PAR': ['#cccccc', '#d9d9d9', '#e6e6e6', '#efefef', '#f3f3f3', '#f7f7f7'],
          'VIR': ['#cccccc', '#d9d9d9', '#e6e6e6', '#efefef', '#f3f3f3', '#f7f7f7'],
      }

      table_html = '<div class="player-stats-container">'
      table_html += '<table class="player-stats-table">'
      
      table_html += '<thead><tr>'
      for col in display_columns:
          table_html += f'<th>{col}</th>'
      table_html += '</tr></thead>'
      
      # Calculate rankings for each numeric column
      numeric_columns = {}
      for col in display_columns:
          if col not in ['Team', 'Player', 'MIN']:
              try:
                  values = df[col].astype(float)
                  sorted_values = sorted(values.unique(), reverse=True)
                  rank_dict = {value: idx for idx, value in enumerate(sorted_values)}
                  numeric_columns[col] = {
                      'rank_dict': rank_dict,
                      'total_ranks': len(sorted_values) - 1
                  }
              except:
                  continue
      
      for _, row in df.iterrows():
          table_html += '<tr>'
          for col in display_columns:
              value = row[col]
              
              if col in ['Team', 'Player']:
                  table_html += f'<td style="color: #1a1f36; font-weight: 700;white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:0;">{value}</td>'
              elif col in numeric_columns and not pd.isna(value):
                  try:
                      float_val = float(value)
                      rank = numeric_columns[col]['rank_dict'].get(float_val, 0)
                      
                      team_shades = team_color_shades[team_code]
                      base_color = team_shades[min(rank, len(team_shades)-1)]
                      
                      gradient_style = f"""
                      background: linear-gradient(to bottom, 
                          rgba(300, 300, 300, 1),
                          {base_color}
                      )
                      """
                      
                      if col.endswith('%'):
                          formatted_value = f"{float_val:.0f}%" if float_val >= 1 else f"{float_val * 100:.0f}%"
                      else:
                          formatted_value = f"{float_val:.1f}"
                      
                      table_html += f'<td style="color: #1a1f36; text-align: center; {gradient_style}">{formatted_value}</td>'
                  except:
                      table_html += f'<td>{value}</td>'
              else:
                  table_html += f'<td style="color: #1a1f36;text-align: center">{value}</td>'
                  
          table_html += '</tr>'
      table_html += '</table></div>'
      
      return table_html

  # Display tables based on selected view
   if view_options[selected_view] == 'All':
      # Original two-column layout
      _, team2_stats_area, team1_stats_area = st.columns([3.8, 5.2, 5.2])
      
      with team1_stats_area:
          display_columns = ['Player', 'MIN', 'PTS', 'REB', '3FG']
          home_player_stats = filtered_player_statsTeam1[filtered_player_statsTeam1['Team'] == home_team]
          
          # Round numerical values
          for col in ['MIN', 'PTS', 'REB', '3FG']:
              if col in home_player_stats.columns:
                  home_player_stats[col] = home_player_stats[col].round(2)
          
          home_table_html = create_player_stats_html(home_player_stats[display_columns], display_columns, home_team)
          home_table_html = home_table_html.replace('class="player-stats-container"', 'class="player-stats-container all-view left-table"')
          st.markdown(home_table_html, unsafe_allow_html=True)
      
      with team2_stats_area:
          away_player_stats = filtered_player_statsTeam2[filtered_player_statsTeam2['Team'] == away_team]
          
          # Round numerical values
          for col in ['MIN', 'PTS', 'REB', '3FG']:
              if col in away_player_stats.columns:
                  away_player_stats[col] = away_player_stats[col].round(2)
          
          away_table_html = create_player_stats_html(away_player_stats[display_columns], display_columns, away_team)
          away_table_html = away_table_html.replace('class="player-stats-container"', 'class="player-stats-container all-view right-table"')
          st.markdown(away_table_html, unsafe_allow_html=True)

   else:
      # Single team view
      _, single_team_area = st.columns([3.8, 10.42])
      
      with single_team_area:
          display_columns = ['Player', 'MIN', 'PTS', 'OREB', 'DREB', 'REB', 'TO', 
                          '2FG', '2FGA', '2PT%', '3FG', '3FGA', '3PT%', 'FT', 'FTA', 'FT%']
          
          if view_options[selected_view] == 'team1':
              selected_data = filtered_player_statsTeam1[filtered_player_statsTeam1['Team'] == home_team]
          else:
              selected_data = filtered_player_statsTeam2[filtered_player_statsTeam2['Team'] == away_team]
          
          # Round numerical values
          numerical_cols = ['MIN', 'PTS', 'OREB', 'DREB', 'REB', 'TO', '2FGM', '2FGA', '2PT%',
                          '3FG', '3FGA', '3PT%', 'FTM', 'FTA', 'FT%']
          for col in numerical_cols:
              if col in selected_data.columns:
                  selected_data[col] = selected_data[col].round(2)
          
          team_code = home_team if view_options[selected_view] == 'team1' else away_team
          table_html = create_player_stats_html(selected_data[display_columns], display_columns, team_code)
          table_html = table_html.replace('class="player-stats-container"', 'class="player-stats-container single-team"')
          st.markdown(table_html, unsafe_allow_html=True)

































def render_stats_tables_eurocup(selected_matchup, matchups, simulation_results_df_eurocup, table_key_prefix=""):
   simulation_results_df = st.session_state.get('simulation_results_df')
   if simulation_results_df is None:
       st.error("Unable to load simulation results")
       return
   
   matchup_data = simulation_results_df_eurocup[simulation_results_df_eurocup['Matchup'] == selected_matchup].iloc[0]
   
   home_logo = matchup_data['Home_Logo']
   away_logo = matchup_data['Away_Logo']
   home_team = matchup_data['Home_Team']
   away_team = matchup_data['Away_Team']
   home_code2 = matchup_data['Home_Code']
   away_code2 = matchup_data['Away_Code']
   
   # Define team colors dictionary 
   eurocup_team_colors = {
    'LIE': '#8b1538',  # Lietkabelis
    'ARI': '#ffd700',  # Aris
    'BAH': '#0066b3',  # Bahcesehir
    'BES': '#000000',  # Besiktas
    'BUD': '#003874',  # Buducnost
    'LJU': '#008751',  # Cedevita Olimpija
    'JLB': '#e31837',  # JL Bourg
    'TRE': '#000000',  # Dolomiti Energia Trento
    'CAN': '#fdb927',  # Gran Canaria
    'HJE': '#c8102e',  # Hapoel Jerusalem
    'HTA': '#ec1c24',  # Hapoel Tel Aviv
    'JOV': '#006241',  # Joventut
    'ULM': '#f47920',  # Ulm
    'SOP': '#ffd700',  # Sopot
    'TTK': '#00b4e3',  # Turk Telekom
    'CLU': '#000000',  # Cluj
    'VNC': '#7b2132',  # Venice
    'PAM': '#f47a38',  # Valencia
    'VEO': '#000000',  # Hamburg
    'WOL': '#00a79d'   # Wolves
}

# Light version of team colors
   eurocup_team_colors_light = {
    'LIE': '#ffd6e0',  # Light Burgundy (darker)
    'ARI': '#ffe4b3',  # Light Yellow (darker)
    'BAH': '#cce6ff',  # Light Blue (darker)
    'BES': '#e6e6e6',  # Light Gray (darker)
    'BUD': '#cce0ff',  # Light Navy (darker)
    'LJU': '#ccffe0',  # Light Green (darker)
    'JLB': '#ffd0d6',  # Light Red (darker)
    'TRE': '#e6e6e6',  # Light Gray (darker)
    'CAN': '#ffe4b3',  # Light Yellow (darker)
    'HJE': '#ffd0d4',  # Light Red (darker)
    'HTA': '#ffd0d2',  # Light Red (darker)
    'JOV': '#ccffe0',  # Light Green (darker)
    'ULM': '#ffe0cc',  # Light Orange (darker)
    'SOP': '#ffe4b3',  # Light Yellow (darker)
    'TTK': '#ccf2ff',  # Light Blue (darker)
    'CLU': '#e6e6e6',  # Light Gray (darker)
    'VNC': '#ffd6e0',  # Light Burgundy (darker)
    'PAM': '#ffe0cc',  # Light Orange (darker)
    'VEO': '#e6e6e6',  # Light Gray (darker)
    'WOL': '#ccfff8'   # Light Turquoise (darker)
}

# Short team names
   team_name_short = {
    'LIE': 'LIETKABELIS',
    'ARI': 'ARIS MIDEA',
    'BAH': 'BAHCESEHIR',
    'BES': 'BESIKTAS',
    'BUD': 'BUDUCNOST',
    'LJU': 'CEDEVITA',
    'JLB': 'JL BOURG',
    'TRE': 'DOLOMITI',
    'CAN': 'GRAN CANARIA',
    'HJE': 'HAPOEL BANK',
    'HTA': 'HAPOEL TEL AVIV',
    'JOV': 'JOVENTUT',
    'ULM': 'RATIOPHARM',
    'SOP': 'TREFL SOPOT',
    'TTK': 'TURK TELEKOM',
    'CLU': 'U-BT CLUJ',
    'VNC': 'REYER VENICE',
    'PAM': 'VALENCIA',
    'VEO': 'VEOLIA TOWERS',
    'WOL': 'WOLVES'
}


   
   team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_eurocup()
   filtered_team_stats = team_stats[team_stats['Matchup'] == selected_matchup]
   filtered_player_statsTeam1 = player_statsTeam1[player_statsTeam1['Matchup'] == selected_matchup]
   filtered_player_statsTeam2 = player_statsTeam2[player_statsTeam2['Matchup'] == selected_matchup]
   filtered_player_statsTeam1 = player_statsTeam1[player_statsTeam1['Matchup'] == selected_matchup].copy()
   filtered_player_statsTeam2 = player_statsTeam2[player_statsTeam2['Matchup'] == selected_matchup].copy()

# Rename the column in both DataFrames
   filtered_player_statsTeam1 = filtered_player_statsTeam1.rename(columns={'3FGM': '3FG', '2FGM': '2FG', 'FTM':'FT'})
   filtered_player_statsTeam2 = filtered_player_statsTeam2.rename(columns={'3FGM': '3FG', '2FGM': '2FG', 'FTM':'FT'})

   # Add state management for HCA and possessions
   if 'hca' not in st.session_state:
       st.session_state.hca = 80
   if 'possessions' not in st.session_state:
       st.session_state.possessions = 72
   
   st.markdown("""
       <style>
       .table-container {
           border: 3px !important;;
           border-radius: 16px;
           background-color: white;
           margin: -5px -10px 10px -10px;
           box-shadow: 0 0 0 1px rgba(0,0,0,0.08);

       }

       .logo-cell {
           display: flex;
           flex-direction: column;
           align-items: center;
           justify-content: center;
           padding: 10px;
           background-color: white;
           border-radius: 8px;
           box-shadow: 0 4px 20px rgba(100, 100, 100, 3.5);
           margin-bottom: 8px;
           margin-top: -15px !important;
       }

       .logo-cell img {
           width: 200px;
           height: 200px;
           object-fit: contain;
       }

       .team-name-box {
           background-color: white;
           border-radius: 8px;
           padding: 2px;
           box-shadow: 0 4px 10px rgba(100, 100, 100, 1.5);
           margin-bottom: 6px;
           width: 100%;
           text-align: center;
       }

       .team-name {
           font-weight: 700;
           font-size: 11px !important;
           font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
           color: rgba(0,0,0,0.9);
           white-space: nowrap;
           overflow: hidden;
           text-overflow: ellipsis;
       }
.team-stats-eurocup-container {
    background-color: white;
    border-radius: 16px;
    color: rgb(26, 31, 54);
    box-shadow: 0 4px 12px rgba(100, 100, 100, .5);
    margin-top: -50px !important;
    margin-left: -60px !important;
    border: 2px solid white !important; 
    overflow: hidden;
    text-align: center;
    border:none;
    border-collapse: collapse;
    border-radius: 16px;
    overflow: hidden;
}

.team-stats-eurocup-table {
    width: 100%;
    border-collapse: collapse;
    border-spacing: 0;
    box-shadow: 0 0 15px rgba(100, 100, 100, 1);
}

/* Enhanced Table header styles */
.team-stats-eurocup-container th {
    color: rgb(26, 31, 54); 
    font-weight: 800;
    font-size: 14px;
    padding: 6px 4px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    position: relative;
    z-index: 1;
}

/* Add hover effect for rows */
.team-stats-eurocup-container tr:hover {
    background: linear-gradient(145deg, #f8f9fa, #f1f3f5) !important;
    transition: background 0.2s ease-in-out !important;
}

/* Preserve background for header row */
.team-stats-eurocup-container thead tr:hover {
    background: none !important;
}

/* Add darker borders for specific rows */
.team-stats-eurocup-container tr:nth-child(1) {
    border-top: 8px solid #e0e0e0 !important;
}

.team-stats-eurocup-container tr:nth-child(2) {
    border-top: 8px solid #e0e0e0;
}

.team-stats-eurocup-container tr:nth-child(6) {
    border-top: 8px solid #e0e0e0;
}

.team-stats-eurocup-container tr:nth-child(9) {
    border-top: 8px solid #e0e0e0;
}

/* Add a subtle line between header cells */
.team-stats-eurocup-container th:not(:last-child) {
    border-right: 1px solid #e0e0e0;
}
/* Highlighting styles */
.highlight {
    background-color: #fff4b3;
    position: relative;
    font-weight: 900;
}

.team-name {
    font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    font-weight: 800;
    font-size: 12px;
    color: #1a1f36;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-transform: uppercase;
    letter-spacing: 0.1px;
}


       </style>
   """, unsafe_allow_html=True)
   
   first_row = simulation_results_df_eurocup[simulation_results_df_eurocup['Matchup'] == selected_matchup].iloc[0]
   st.markdown('<div class="eurocup_tab">', unsafe_allow_html=True)

   team_stats_area, spacing1, logo_area,  stats_area = st.columns([1.4, 0.9, 4,  2.6])
   
   with team_stats_area:
       # Team Stats Table (Full Width)
       team_stats_df = pd.DataFrame(first_row['SimmedTeamStats']).T
       # Reset the index to make the current index a column
       team_stats_df = team_stats_df.reset_index()
       # Set the first row as the new column names
       team_stats_df.columns = team_stats_df.iloc[0]
       # Drop the first row (since it's now the column names)
       team_stats_df = team_stats_df.drop(0).reset_index(drop=True) 
       team_stats_df['PTS'] = team_stats_df['Points']
       team_stats_df['3ptA'] = team_stats_df['3pt Attempts']
       team_stats_df['3ptM'] = team_stats_df['3pt Makes']
       team_stats_df['2ptA'] = team_stats_df['2pt Attempts']
       team_stats_df['2ptM'] = team_stats_df['2pt Makes']
       team_stats_df['FTA'] = team_stats_df['FT Attempts']
       team_stats_df['FTM'] = team_stats_df['FT Makes']
       team_stats_df['TO'] = team_stats_df['Turnovers']
       team_stats_df['FTA%'] = team_stats_df['FTA%'] * 100
       team_stats_df['OREB%'] = team_stats_df['OR%'] *100
       team_stats_df['2pt%'] = team_stats_df['2pt%'] * 100
       team_stats_df['3pt%'] = team_stats_df['3pt%'] *100
       team_stats_df['FT%'] = team_stats_df['FT%'] *100
       team_stats_df['TO%'] = team_stats_df['Turnovers']/team_stats_df['Possessions'] *100
       team_stats_df['eFG%'] = (team_stats_df['2ptM'] + 1.5* team_stats_df['3ptM'])/(team_stats_df['2ptA'] + team_stats_df['3ptA']) *100
       team_stats_df = team_stats_df.rename(columns={'Metric': 'Team'})
       team_stats_df = team_stats_df[['Team','PTS','eFG%','TO%','OREB%','FTA%','3pt%', '2pt%','FT%','3ptM','3ptA','2ptM','2ptA','FTM','FTA']]

       # When doing the final transpose, keep the index
       team_stats_df = team_stats_df.set_index('Team').T.reset_index()
       team_stats_df = team_stats_df.rename(columns={0: ''})
       cols = team_stats_df.columns.tolist()
       cols[1], cols[2] = cols[2], cols[1]  # Swap the columns
       team_stats_df = team_stats_df[cols]
       # Convert team colors to RGB format for CSS variables
       

       # Convert team colors to RGB format for CSS variables
       home_code = home_code2
       away_code = away_code2

    # Explicitly create RGB values using EuroCup team colors
       local_team_colors = dict(eurocup_team_colors)

    # Use local_team_colors instead of euroleague_team_colors
       away_team_color = local_team_colors.get(away_code2, '#f0f0f0')
       home_team_color = local_team_colors.get(home_code2, '#f0f0f0')

    # Create the CSS variables
       team_css = f"""
    <style>
        .team-stats-eurocup-container th:nth-child(1) {{
            background: linear-gradient(to bottom, 
        rgb(255, 255, 255), 
        rgb(245, 245, 247);
        }}

        .team-stats-eurocup-container th:nth-child(2) {{
            background: linear-gradient(to bottom, 
                rgba(255, 255, 255, 0.7),
                {away_team_color}
            ) !important;
        }}

        .team-stats-eurocup-container th:nth-child(3) {{
            background: linear-gradient(to bottom,
                rgba(255, 255, 255, 0.7),
                {home_team_color}
            ) !important;
        }}
       </style>
       """

       # Apply the CSS
       st.markdown(team_css, unsafe_allow_html=True)
       # Convert team colors to RGB format for CSS variables
       team_html = """
       <div class="team-stats-eurocup-container">
           <table style="width: 100%">
               <colgroup>
                   <col style="width: 10%">
                   <col style="width: 45%">
                   <col style="width: 45%">
               </colgroup>
               <thead><tr>{}</tr></thead>
               <tbody>{}</tbody>
           </table>
       </div>
       """

       
       team_header = f"""<th>{team_stats_df.columns[0]}</th>
<th>
   <div style="display: flex; align-items: center; gap: 2px; justify-content: center;">
       <div style="width: 40px; height: 40px; display: flex; align-items: center; padding: 2px;">
           <img src="{away_logo}" alt="Logo" style="width: 100%; height: 650px; object-fit: contain;">
       </div>
       <span>{team_stats_df.columns[1]}</span>
   </div>
</th>
<th>
   <div style="display: flex; align-items: center; gap: 2px; justify-content: center;">
       <div style="width: 40px; height: 40px; display: flex; align-items: center; padding: 2px;">
           <img src="{home_logo}" alt="Logo" style="width: 100%; height: 650px; object-fit: contain;">
       </div>
       <span>{team_stats_df.columns[2]}</span>
   </div>
</th>"""

       # CSS for highlighting
       highlight_css = """
       <style>
           .highlight {
               position: relative;
               font-weight: 900;
           }
       </style>
       """

       # Add the CSS to the Streamlit app
       st.markdown(highlight_css, unsafe_allow_html=True)

       # Generate the table rows with conditional highlighting
       team_rows = ''.join(
    f'<tr class="{" ".join(filter(None, [
        "first-row" if index == 0 else "",
        "section-start" if index == 1 else "",
        "key-section" if 1 <= index <= 4 else ""
    ]))}">' +
    ''.join(
        f'<td class="numeric" style="text-align: center; font-weight: 1000; font-size: 12px;">{value}</td>' 
        if idx == 0
        else f'<td class="numeric" style="text-align: center"><div style="margin-left: -2px;font-size: 12px;margin-right:-5px;"><span class="highlight" style="padding: 3px 3px; border-radius: 4px; background-color: {eurocup_team_colors_light[team_stats_df.columns[1]] if (idx == 1 and ((value > row[2] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[2] and row.iloc[0] in ["TO%", "TO"]))) else "transparent"}">{f"{value:.1f}%" if str(row.iloc[0]).endswith("%") else f"&nbsp;{value:>5.1f}&nbsp;"}</span>{f"<img src=\'{away_logo}\' style=\'width: 25px; height: 25px; margin-left: 2px; vertical-align: middle;\'/>" if (idx == 1 and ((value > row[2] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[2] and row.iloc[0] in ["TO%", "TO"]))) else ""}</div></td>' 
        if isinstance(value, (int, float)) and idx == 1
        else f'<td class="numeric" style="text-align: center"><div style="margin-left: -2px;font-size: 12px;margin-right:-5px;"><span class="highlight" style="padding: 3px 3px; border-radius: 4px; background-color: {eurocup_team_colors_light[team_stats_df.columns[2]] if (idx == 2 and ((value > row[1] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[1] and row.iloc[0] in ["TO%", "TO"]))) else "transparent"}">{f"{value:.1f}%" if str(row.iloc[0]).endswith("%") else f"&nbsp;{value:>5.1f}&nbsp;"}</span>{f"<img src=\'{home_logo}\' style=\'width: 25px; height: 25px; margin-left: 2px; vertical-align: middle;\'/>" if (idx == 2 and ((value > row[1] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[1] and row.iloc[0] in ["TO%", "TO"]))) else ""}</div></td>' 
        if isinstance(value, (int, float)) and idx == 2
        else f'<td style="text-align: center">{value}</td>'
        for idx, (col, value) in enumerate(row.items())
    ) + 
    '</tr>'
    for index, row in team_stats_df.iterrows()
)

       # Render the table
       st.markdown(team_html.format(team_header, team_rows), unsafe_allow_html=True)
   
       with logo_area:
          away_logo_col, vs_col, home_logo_col, = st.columns([1, 0.2, 1])
          
          with away_logo_col:
              st.markdown(
                  f"""
                  <div class="logo-cell" style="background-color: {eurocup_team_colors[away_code2]}">
                      <img src="{away_logo}" alt="{away_team} Logo">
                  </div>
                  <div class="team-name-box">
                      <div class="team-name">{team_name_short[away_code2]}</div>
                  </div>
                  """,
                  unsafe_allow_html=True
              )
          
          with vs_col:
              st.markdown("""
              <div style='display: flex; justify-content: center; align-items: center;'>
                  <div style='background-color: white; 
                            border-radius: 8px; 
                            padding: 3px 8px; 
                            box-shadow: 0 4px 12px rgba(100, 100, 100, .4);
                            margin-top: 45px;'>
                      <span style='font-size: 16px; color: #1a1f36; font-weight: 800;'>@</span>
                  </div>
              </div>
              """, unsafe_allow_html=True)
          
          with home_logo_col:
              st.markdown(
                  f"""
                  <div class="logo-cell" style="background-color: {eurocup_team_colors[home_code2]}">
                      <img src="{home_logo}" alt="{home_team} Logo">
                  </div>
                  <div class="team-name-box">
                      <div class="team-name">{team_name_short[home_code2]}</div>
                  </div>
                  """,
                  unsafe_allow_html=True
              )


   with stats_area:
       first_row = simulation_results_df_eurocup[simulation_results_df_eurocup['Matchup'] == selected_matchup].iloc[0]
       summary_stats_df = pd.DataFrame(first_row['SimmedTeamStats'][-3:]).T
       
       summary_stats_df.columns = summary_stats_df.iloc[0]
       summary_stats_df = summary_stats_df.drop(summary_stats_df.index[0])
       summary_stats_df = summary_stats_df.rename(columns={'Total Adjusted': 'Total'})
       summary_stats_df = summary_stats_df[['Spread', 'Total', 'Money']]
       
       html_table = """
       <div class="summary-stats-eurocup">  <!-- or summary-stats-eurocup -->
           <table width="100%">
               <thead>
                   <tr>
                       <th>Team</th>
"""
       for col in summary_stats_df.columns:
           html_table += f"<th>{col}</th>"
       
       html_table += """
                   </tr>
               </thead>
               <tbody>
       """
       
       for idx, row in summary_stats_df.iterrows():
           html_table += "<tr>"

           logo_to_use = home_logo if idx == summary_stats_df.index[0] else away_logo
           team_name = home_code2 if idx == summary_stats_df.index[0] else away_code2

           html_table += f'''
               <td>
                   <div style="display: flex; align-items: center; justify-content: center; gap: 6px; padding: 5px; margin-left:0px;">
                       <div style="width: 30px; height: 30px; display: flex; align-items: center;">
                           <img src="{logo_to_use}" alt="Logo" style="width: 100%; height: auto; object-fit: contain;margin-left:0px;">
                       </div>
                       <span style="font-size: 14px; font-weight: 800; color: rgba(0,0,0,0.7);">{team_name}</span>
                   </div>
               </td>
           '''

           for col, val in row.items():
               if isinstance(val, (int, float)):
                   if val > 1:
                       style_class = "metric-high"
                   elif val > 1:
                       style_class = "metric-medium"
                   else:
                       style_class = "metric-low"

                   if col == "Money":
                       html_table += f'<td class="{style_class}">{val:.2f}</td>'
                   else:
                       html_table += f'<td class="{style_class}">{val:.1f}</td>'
               else:
                   html_table += f"<td>{val}</td>"
           html_table += "</tr>"

       html_table += """
               </tbody>
           </table>
       </div>
       """

       st.markdown(html_table, unsafe_allow_html=True)
   st.markdown("<div style='margin: 0px 0;'></div>", unsafe_allow_html=True)


 
# Create a second row of columns for player stats table
  # Create a second row of columns for player stats table
   # Create a second row of columns for player stats table
   # Create a second row of columns for player stats table
   _, select_col, _ = st.columns([.001, .001, .001])  
  
   with select_col:
      # Get team names from matchup data
      first_row = simulation_results_df_eurocup[simulation_results_df_eurocup['Matchup'] == selected_matchup].iloc[0]
      away_team = first_row['Away_Code']
      home_team = first_row['Home_Code']
      
      # Unified CSS block
      st.markdown("""
          <style>
          /* Button Styles */
          /* Button container styling */
div.stButton {
   margin-top: -485px !important;
   margin-left: -50px !important;  /* This moves buttons up */
   position: relative !important;
   z-index: 2 !important;  /* Ensure buttons stay on top */
   padding: 0 !important;  /* Remove padding */
   margin-bottom: -8px !important;  /* Reduce space between buttons */
}

/* Individual button styling */
div.stButton > button {
   width: 100%;
   background-color: #1a1f36;
   border: 3px solid #1a1f36;  /* Reduced border from 5px to 2px */
   color: white;
   font-weight: 700;
   border-radius: 8px;
   font-size: 6px !important;
   padding: 3px 3px !important;  /* Reduced padding */
   min-height: 20px !important;  /* Reduced height */
   height: 20px !important;  /* Set explicit height */
   line-height: 20px !important;  /* Match line height to height */
}

div.stButton > button:hover {
   border-color: #2d63e2;
   color: #2d63e2;
   background-color: rgba(45, 99, 226, 0.1);
}

div.stButton > button:focus {
   box-shadow: none;
   background-color: rgba(45, 99, 226, 0.1);
   color: #2d63e2;
   border-color: #2d63e2;
}

/* Base Table Styles */
.player-stats-container {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 0 15px rgba(100, 100, 100, .5);
    margin-top: -470px !important;
}

.player-stats-table {
    font-size: 11px !important;
    width: 100% !important;
    table-layout: fixed !important;
    border-spacing: 0 !important;  /* Added to ensure consistent spacing */
    border-collapse: collapse !important;  /* Added to ensure consistent spacing */
}

/* Increased heights for headers */
.player-stats-table th {
    font-weight: 700 !important;
    background-color: white !important;
    font-size: 12px !important;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    height: 20px !important;  /* Increased from 30px */
    line-height: 5px !important;  /* Added to match height */
    vertical-align: middle !important;
}

/* Increased heights for cells */
.player-stats-table td {
    padding: 8px 4px !important;  /* Increased top/bottom padding */
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    height: 35px !important;  /* Increased from 25px */
    line-height: 15px !important;  /* Added to match height */
    vertical-align: middle !important;
}

/* Add some subtle borders for better readability */
.player-stats-table tr {
    border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
}

/* All View Table Styles */
.all-view.player-stats-container {
    min-width: 310px !important;
    width: 310px !important;
    max-width: 310px !important;
    overflow: hidden !important;  /* Prevent scrolling in All view */
}

.all-view.player-stats-container.left-table {
    position: relative !important;
    left: 30px !important;
}

.all-view.player-stats-container.right-table {
    position: relative !important;
    margin-left: 0px !important;
}

.all-view .player-stats-table td:first-child,
.all-view .player-stats-table th:first-child {
    width: 120px !important;
    background: rgb(255, 255, 255) !important;  /* Pure white background */
    border-right: 1px solid rgba(200, 200, 200, 0.4) !important;  /* Slightly more visible separator */
    box-shadow: 1px 0 2px rgba(0, 0, 0, 0.05) !important;  /* Subtle shadow for depth */
}

/* Also ensure the text remains clearly visible */
.player-stats-table td:first-child {
    color: #1a1f36 !important;  /* Darker text color for better contrast */
    font-weight: 700 !important;
}

/* Add hover effect for more metallic feel */
.all-view .player-stats-table td:first-child:hover {
    background: linear-gradient(145deg, #f5f5f5, #e8e8e8) !important;
}



/* Individual Team View Styles */
.player-stats-container.single-team {
    min-width: 620px !important;
    width: 620px !important;
    max-width: 620px !important;
    margin-right: 0px !important;
    overflow-x: scroll !important;
}

/* Individual view specific column widths */
.single-team .player-stats-table {
    min-width: 600px !important; /* Make table wider than container to enable scroll */
}

.single-team .player-stats-table td:first-child,
.single-team .player-stats-table th:first-child {
    width: 140px !important;
    text-align: left !important;
    padding-left: 8px !important;
    position: sticky !important;
    left: 0 !important;
    background: white !important;
    z-index: 1 !important;
}

.single-team .player-stats-table td:not(:first-child),
.single-team .player-stats-table th:not(:first-child) {
    width: 50px !important;  /* Wider columns for individual view */
}

/* Custom scrollbar for individual team view */
.player-stats-container.single-team::-webkit-scrollbar {
    height: 8px !important;
}

.player-stats-container.single-team::-webkit-scrollbar-track {
    background: #f1f1f1 !important;
    border-radius: 4px !important;
}

.player-stats-container.single-team::-webkit-scrollbar-thumb {
    background: #888 !important;
    border-radius: 4px !important;
}

.player-stats-container.single-team::-webkit-scrollbar-thumb:hover {
    background: #555 !important;
}
          </style>
      """, unsafe_allow_html=True)
      
      # Create three columns for the buttons
      btn1_eurocup, btn3_eurocup, btn2_eurocup = st.columns([0.01, 0.01, 0.01])
      
      # Initialize session state for button selection
      if 'selected_view' not in st.session_state:
          st.session_state.selected_view = 'All'
      
      # Create the buttons
      with btn1_eurocup:
          if st.button('All', key='game_view_btn_eurocup'):
              st.session_state.selected_view = 'All'
      with btn2_eurocup:
          if st.button(home_team, key='home_team_btn_eurocup'):
              st.session_state.selected_view = 'Home'
      with btn3_eurocup:
          if st.button(away_team, key='away_team_btn_eurocup'):
              st.session_state.selected_view = 'Away'
      
      view_options = {
          'All': 'All',
          'Home': 'team1',
          'Away': 'team2'
      }
      
      selected_view = st.session_state.selected_view

   def create_player_stats_html(df, display_columns, team_code):
      # Create color shades dictionary based on team base colors
      team_color_shades = {
    # Burgundy shades
    'LIE': ['#cc99a8', '#d6adb8', '#e0c1c8', '#ebd5d9', '#f5e9eb', '#ffeaef'],
    
    # Yellow shades
    'ARI': ['#ffd966', '#ffe180', '#ffed99', '#fff4cc', '#fff7e0', '#fff9e6'],
    'SOP': ['#ffd966', '#ffe180', '#ffed99', '#fff4cc', '#fff7e0', '#fff9e6'],
    
    # Blue shades
    'BAH': ['#99c2ff', '#b3d1ff', '#cce0ff', '#e6f0ff', '#f0f5ff', '#f5f9ff'],
    'TTK': ['#99e2ff', '#b3e9ff', '#ccf0ff', '#e6f7ff', '#f0fbff', '#f5fdff'],
    
    # Black/Gray shades
    'BES': ['#cccccc', '#d9d9d9', '#e6e6e6', '#f0f0f0', '#f5f5f5', '#fafafa'],
    'TRE': ['#cccccc', '#d9d9d9', '#e6e6e6', '#f0f0f0', '#f5f5f5', '#fafafa'],
    'CLU': ['#cccccc', '#d9d9d9', '#e6e6e6', '#f0f0f0', '#f5f5f5', '#fafafa'],
    'VEO': ['#cccccc', '#d9d9d9', '#e6e6e6', '#f0f0f0', '#f5f5f5', '#fafafa'],
    
    # Navy shades
    'BUD': ['#99b8e6', '#b3c6eb', '#ccd4f0', '#e6e2f5', '#f0f1fa', '#f5f5ff'],
    
    # Green shades
    'LJU': ['#99d4b3', '#b3dcc6', '#cce5d9', '#e6edeb', '#f0f6f5', '#f5fffa'],
    'JOV': ['#99c2ae', '#b3ccc1', '#ccd6d4', '#e6ebe7', '#f0f5f3', '#f5fffa'],
    
    # Red shades
    'JLB': ['#ff99a3', '#ffb3ba', '#ffccd1', '#ffe6e8', '#fff0f1', '#fff5f6'],
    'HJE': ['#ff9999', '#ffb3b3', '#ffcccc', '#ffe6e6', '#fff0f0', '#fff5f5'],
    'HTA': ['#ff9999', '#ffb3b3', '#ffcccc', '#ffe6e6', '#fff0f0', '#fff5f5'],
    
    # Yellow/Gold shades
    'CAN': ['#ffd480', '#ffdb99', '#ffe6b3', '#fff0cc', '#fff5e6', '#fff9f0'],
    
    # Orange shades
    'ULM': ['#ffb380', '#ffc299', '#ffd1b3', '#ffe0cc', '#fff0e6', '#fff5f0'],
    'PAM': ['#ffb380', '#ffc299', '#ffd1b3', '#ffe0cc', '#fff0e6', '#fff5f0'],
    
    # Burgundy shades (Venice)
    'VNC': ['#cc99a8', '#d6adb8', '#e0c1c8', '#ebd5d9', '#f5e9eb', '#ffeaef'],
    
    # Turquoise shades
    'WOL': ['#99e6e0', '#b3ebe7', '#ccf0ee', '#e6f5f4', '#f0faf9', '#f5fffd']
      }

      table_html = '<div class="player-stats-container">'
      table_html += '<table class="player-stats-table">'
      
      table_html += '<thead><tr>'
      for col in display_columns:
          table_html += f'<th>{col}</th>'
      table_html += '</tr></thead>'
      
      # Calculate rankings for each numeric column
      numeric_columns = {}
      for col in display_columns:
          if col not in ['Team', 'Player', 'MIN']:
              try:
                  values = df[col].astype(float)
                  sorted_values = sorted(values.unique(), reverse=True)
                  rank_dict = {value: idx for idx, value in enumerate(sorted_values)}
                  numeric_columns[col] = {
                      'rank_dict': rank_dict,
                      'total_ranks': len(sorted_values) - 1
                  }
              except:
                  continue
      
      for _, row in df.iterrows():
          table_html += '<tr>'
          for col in display_columns:
              value = row[col]
              
              if col in ['Team', 'Player']:
                  table_html += f'<td style="color: #1a1f36; font-weight: 700;white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:0;">{value}</td>'
              elif col in numeric_columns and not pd.isna(value):
                  try:
                      float_val = float(value)
                      rank = numeric_columns[col]['rank_dict'].get(float_val, 0)
                      
                      team_shades = team_color_shades[team_code]
                      base_color = team_shades[min(rank, len(team_shades)-1)]
                      
                      gradient_style = f"""
                      background: linear-gradient(to bottom, 
                          rgba(300, 300, 300, 1),
                          {base_color}
                      )
                      """
                      
                      if col.endswith('%'):
                          formatted_value = f"{float_val:.0f}%" if float_val >= 1 else f"{float_val * 100:.0f}%"
                      else:
                          formatted_value = f"{float_val:.1f}"
                      
                      table_html += f'<td style="color: #1a1f36; text-align: center; {gradient_style}">{formatted_value}</td>'
                  except:
                      table_html += f'<td>{value}</td>'
              else:
                  table_html += f'<td style="color: #1a1f36;text-align: center">{value}</td>'
                  
          table_html += '</tr>'
      table_html += '</table></div>'
      
      return table_html

  # Display tables based on selected view
   if view_options[selected_view] == 'All':
      # Original two-column layout
      _, team2_stats_area, team1_stats_area = st.columns([3.8, 5.2, 5.2])
      
      with team1_stats_area:
          display_columns = ['Player', 'MIN', 'PTS', 'REB', '3FG']
          home_player_stats = filtered_player_statsTeam1[filtered_player_statsTeam1['Team'] == home_team]
          
          # Round numerical values
          for col in ['MIN', 'PTS', 'REB', '3FG']:
              if col in home_player_stats.columns:
                  home_player_stats[col] = home_player_stats[col].round(2)
          
          home_table_html = create_player_stats_html(home_player_stats[display_columns], display_columns, home_team)
          home_table_html = home_table_html.replace('class="player-stats-container"', 'class="player-stats-container all-view left-table"')
          st.markdown(home_table_html, unsafe_allow_html=True)
      
      with team2_stats_area:
          away_player_stats = filtered_player_statsTeam2[filtered_player_statsTeam2['Team'] == away_team]
          
          # Round numerical values
          for col in ['MIN', 'PTS', 'REB', '3FG']:
              if col in away_player_stats.columns:
                  away_player_stats[col] = away_player_stats[col].round(2)
          
          away_table_html = create_player_stats_html(away_player_stats[display_columns], display_columns, away_team)
          away_table_html = away_table_html.replace('class="player-stats-container"', 'class="player-stats-container all-view right-table"')
          st.markdown(away_table_html, unsafe_allow_html=True)

   else:
      # Single team view
      _, single_team_area = st.columns([3.8, 10.42])
      
      with single_team_area:
          display_columns = ['Player', 'MIN', 'PTS', 'OREB', 'DREB', 'REB', 'TO', 
                          '2FG', '2FGA', '2PT%', '3FG', '3FGA', '3PT%', 'FT', 'FTA', 'FT%']
          
          if view_options[selected_view] == 'team1':
              selected_data = filtered_player_statsTeam1[filtered_player_statsTeam1['Team'] == home_team]
          else:
              selected_data = filtered_player_statsTeam2[filtered_player_statsTeam2['Team'] == away_team]
          
          # Round numerical values
          numerical_cols = ['MIN', 'PTS', 'OREB', 'DREB', 'REB', 'TO', '2FGM', '2FGA', '2PT%',
                          '3FG', '3FGA', '3PT%', 'FTM', 'FTA', 'FT%']
          for col in numerical_cols:
              if col in selected_data.columns:
                  selected_data[col] = selected_data[col].round(2)
          
          team_code = home_team if view_options[selected_view] == 'team1' else away_team
          table_html = create_player_stats_html(selected_data[display_columns], display_columns, team_code)
          table_html = table_html.replace('class="player-stats-container"', 'class="player-stats-container single-team"')
          st.markdown(table_html, unsafe_allow_html=True)









def render_round_summary(
    simulation_results_df, 
    team_colors, 
    team_name_short, 
    league_name='Euroleague'
):
    # CSS for styling - using unique class names to avoid conflicts
    st.markdown("""
    <style>
    /* Round summary specific styles with unique class names */
    .rs_table-container {
        border: 3px !important;
        border-radius: 16px;
        background-color: white;
        margin: -5px -10px 10px -10px;
        box-shadow: 0 0 0 1px rgba(0,0,0,.2);
    }

    .rs_logo-cell {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(100, 100, 100, 3.5);
        margin-bottom: 8px;
    }

    .rs_logo-cell img {
        width: 60px;
        height: 75px;
        object-fit: contain;
    }

    .rs_team-name-box {
        background-color: white;
        border-radius: 8px;
        padding: 6px;
        box-shadow: 0 4px 10px rgba(100, 100, 100, 1.5);
        margin-bottom: 6px;
        width: 100%;
        text-align: center;
    }

    .rs_team-name {
        font-weight: 800;
        font-size: 11px !important;
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
        color: rgba(26, 31, 54, 0.9);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Dark summary stats table style */
    
    .rs_summary-stats table {
        border-collapse: collapse;
        border-radius: 16px;
        overflow: hidden;
        border: 2px solid white !important;
        background-color: #1a1f36;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        width: 100%;
    }
    
    .rs_summary-stats tr {
        background-color: #1a1f36 !important;  /* Force dark background */
    }
    
    .rs_summary-stats td {
        background-color: #1a1f36 !important;  /* Force dark background */
        padding: 6px;
        text-align: center;
        font-size: 20px;
        vertical-align: middle;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .rs_summary-stats th {
        background-color: #1a1f36 !important;  /* Force dark background */
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 10px;
        text-align: center;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        color: #ffffff;
        padding: 3px;
    }
    
    .rs_summary-stats td div {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 0;
        margin: 0;
    }
    
    .rs_summary-stats td img {
        width: 40px;
        height: 40px;
        vertical-align: middle;
    }
    
    .rs_summary-stats td span {
        font-size: 14px;
        font-weight: 600;
        color: #ffffff !important;
        vertical-align: middle;
    }

    /* Enhanced Leaders section styling */
    .rs_leaders-header {
        background: linear-gradient(to right, #1a1f36, #2c3a5a);
        color: white;
        padding: 4px 8px;
        font-weight: 600;
        font-size: 14px;
        text-align: center;
        text-transform: uppercase;
        border-radius: 6px 6px 0 0;
        letter-spacing: 0.5px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .rs_leaders-list {
        background-color: white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-radius: 0 0 6px 6px;
        overflow: hidden;
        border: 1px solid #e8e8e8;

    }
    
    .rs_leader-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 10px;
        border-bottom: 1px solid #f0f0f0;
        align-items: center;
        background-color: white;
        transition: background-color 0.15s ease;
    }
    
    .rs_leader-row:hover {
        background-color: #f8fafe;
    }
    
    .rs_leader-row:last-child {
        border-bottom: none;
    }
    
    .rs_player-info {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .rs_team-indicator {
        width: 3px;
        height: 20px;
        border-radius: 2px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .rs_player-name {
        font-weight: 500;
        font-size: 12px;
        color: #1a1f36;
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    }
    
    .rs_player-stat {
        font-weight: 700;
        font-size: 14px;
        color: #1a1f36;
        min-width: 30px;
        text-align: right;
        background: linear-gradient(to right, #0d6efd, #3b8ff9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Full-width game info header */
    .rs_game-info-box {
        background-color: white;
        border-radius: 8px;
        padding: 4px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-bottom: 12px;
        margin-top:-15px;
    }
    
    .rs_game-info-icon {
        color: #1a1f36;
        margin-right: 6px;
        font-size: 14px;
    }
    
    .rs_game-info-text {
        font-weight: 600;
        color: #1a1f36;
        font-size: 13px;
    }
    
    /* Filter buttons */
    .rs_filter-buttons {
        display: flex;
        padding: 10px 16px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
        margin-bottom: 10px;
    }
    
    .rs_filter-button {
        background-color: #f1f3f5;
        border: none;
        padding: 6px 14px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 13px;
        color: #495057;
        margin-right: 8px;
    }
    
    .rs_filter-button.active {
        background-color: #1a1f36;
        color: white;
    }

    .rs_game-container {
        margin-bottom: 24px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .rs_versus-symbol {
        display: flex; 
        justify-content: center; 
        align-items: center;
    }

    .rs_versus-box {
        background-color: white; 
        border-radius: 8px; 
        padding: 3px 8px; 
        box-shadow: 0 4px 12px rgba(100, 100, 100, .4);
        margin-top: 30px;
    }

    .rs_versus-text {
        font-size: 16px; 
        color: #1a1f36; 
        font-weight: 800;
    }
    
    /* Game separator */
    .rs_game-separator {
        height: 2px;
        background: linear-gradient(to right, rgba(0,0,0,0.02), rgba(0,0,0,.5), rgba(0,0,0,0.02));
        margin: -15px -15px;
        position: relative;
    }
    
    .rs_game-separator::after {
        content: "";
        position: absolute;
        width: 20px;
        height: 20px;
        background-color: white;
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="%231a1f36"/></svg>');
        background-repeat: no-repeat;
        background-position: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Group games by round
    current_round = simulation_results_df['Round'].max()
    round_games = simulation_results_df[simulation_results_df['Round'] == current_round]

    # Track if we need to add a separator (after the first game)
    first_game = True
    
    # Iterate through each game in the round
    for _, game in round_games.iterrows():
        
        
        home_team = game['Home_Team']
        away_team = game['Away_Team']
        home_code = game['Home_Code']
        away_code = game['Away_Code']
        home_logo = game['Home_Logo']
        away_logo = game['Away_Logo']
        time = game.get('Time', 'N/A')
        arena = game.get('Arena', 'N/A')
        matchup = game['Matchup']
        
        # Get team colors
        home_color = team_colors.get(home_code, '#f0f0f0')
        away_color = team_colors.get(away_code, '#f0f0f0')

        # Prepare summary stats
        summary_stats_df = pd.DataFrame(game['SimmedTeamStats'][-3:]).T
        summary_stats_df.columns = summary_stats_df.iloc[0]
        summary_stats_df = summary_stats_df.drop(summary_stats_df.index[0])
        summary_stats_df = summary_stats_df.rename(columns={'Total Adjusted': 'Total'})
        summary_stats_df = summary_stats_df[['Spread', 'Total', 'Money']]
        st.markdown('<div class="rs_game-separator"></div>', unsafe_allow_html=True)
        # Game info header using Streamlit columns for 50/50 split
        time_col, arena_col = st.columns(2)
        
        with time_col:
            st.markdown(f"""
            <div class="rs_game-info-box">
                <span class="rs_game-info-icon">🕒</span>
                <span class="rs_game-info-text">{time}</span>
            </div>
            """, unsafe_allow_html=True)
            
        with arena_col:
            st.markdown(f"""
            <div class="rs_game-info-box">
                <span class="rs_game-info-icon">🏟️</span>
                <span class="rs_game-info-text">{arena}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Team logos and summary stats
        logo_col, vs_col, home_logo_col, stats_col = st.columns([1, 0.2, 1, 2.3])
        
        with logo_col:
            st.markdown(
                f"""
                <div class="rs_logo-cell" style="background-color: {team_colors.get(away_code, '#f0f0f0')}">
                    <img src="{away_logo}" alt="{away_team} Logo">
                </div>
                <div class="rs_team-name-box">
                    <div class="rs_team-name">{team_name_short.get(away_code, away_team)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with vs_col:
            st.markdown("""
            <div class="rs_versus-symbol">
                <div class="rs_versus-box">
                    <span class="rs_versus-text">@</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with home_logo_col:
            st.markdown(
                f"""
                <div class="rs_logo-cell" style="background-color: {team_colors.get(home_code, '#f0f0f0')}">
                    <img src="{home_logo}" alt="{home_team} Logo">
                </div>
                <div class="rs_team-name-box">
                    <div class="rs_team-name">{team_name_short.get(home_code, home_team)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with stats_col:
            # Creating the dark summary stats table
            html_table = """
            <div class="rs_summary-stats">
                <table>
                    <thead>
                        <tr>
                            <th>TEAM</th>
            """
            for col in summary_stats_df.columns:
                html_table += f"<th>{col.upper()}</th>"
            
            html_table += """
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for idx, row in summary_stats_df.iterrows():
                html_table += "<tr>"

                is_away = idx == away_code or idx == team_name_short.get(away_code, away_team)
                logo_to_use = away_logo if is_away else home_logo
                team_code = away_code if is_away else home_code

                html_table += f'''
                    <td>
                        <div>
                            <img src="{logo_to_use}" alt="{team_code} Logo">
                            <span>{team_code}</span>
                        </div>
                    </td>
                '''

                for col, val in row.items():
                    if isinstance(val, (int, float)):
                        if col == "Money":
                            html_table += f'<td>{val:.2f}</td>'
                        else:
                            html_table += f'<td>{val:.1f}</td>'
                    else:
                        html_table += f"<td>{val}</td>"
                html_table += "</tr>"

            html_table += """
                    </tbody>
                </table>
            </div>
            """

            st.markdown(html_table, unsafe_allow_html=True)
        
        # Get player stats for the matchup
        team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_euroleague(simulation_results_df)
        filtered_player_statsTeam1 = player_statsTeam1[player_statsTeam1['Matchup'] == matchup]
        filtered_player_statsTeam2 = player_statsTeam2[player_statsTeam2['Matchup'] == matchup]
        
        # Combine player stats from both teams for game-level top 5
        combined_player_stats = pd.concat([filtered_player_statsTeam1, filtered_player_statsTeam2])
        
        # Get top players
        top_players_pts = (
            combined_player_stats.sort_values('PTS', ascending=False)
            .drop_duplicates('Player')
            .head(5)[['Player', 'Team', 'PTS']]
        )
        top_players_reb = (
            combined_player_stats.sort_values('REB', ascending=False)
            .drop_duplicates('Player')
            .head(5)[['Player', 'Team', 'REB']]
        )
        top_players_3fg = (
            combined_player_stats.sort_values('3FGM', ascending=False)
            .drop_duplicates('Player')
            .head(5)[['Player', 'Team', '3FGM']]
        )
        
        # Leaders row with three columns of equal width
        leader_col1, leader_col2, leader_col3 = st.columns(3)
        
        # Points Leaders
        with leader_col1:
            st.markdown('<div class="rs_leaders-header">POINTS LEADERS</div>', unsafe_allow_html=True)
            st.markdown('<div class="rs_leaders-list">', unsafe_allow_html=True)
            for _, row in top_players_pts.iterrows():
                player = row['Player']
                team = row.get('Team', '')
                color = team_colors.get(team, '#1e293b')
                
                st.markdown(f"""
                <div class="rs_leader-row">
                    <div class="rs_player-info">
                        <div class="rs_team-indicator" style="background-color: {team_colors.get(team, '#1e293b')};"></div>
                        <span class="rs_player-name">{player}</span>
                    </div>
                    <span class="rs_player-stat">{row["PTS"]:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Rebounds Leaders
        with leader_col2:
            st.markdown('<div class="rs_leaders-header">REBOUNDS LEADERS</div>', unsafe_allow_html=True)
            st.markdown('<div class="rs_leaders-list">', unsafe_allow_html=True)
            for _, row in top_players_reb.iterrows():
                player = row['Player']
                team = row.get('Team', '')
                color = team_colors.get(team, '#1e293b')
                
                st.markdown(f"""
                <div class="rs_leader-row">
                    <div class="rs_player-info">
                        <div class="rs_team-indicator" style="background-color: {team_colors.get(team, '#1e293b')};"></div>
                        <span class="rs_player-name">{player}</span>
                    </div>
                    <span class="rs_player-stat">{row["REB"]:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 3-Pointers Leaders
        with leader_col3:
            st.markdown('<div class="rs_leaders-header">3-POINT LEADERS</div>', unsafe_allow_html=True)
            st.markdown('<div class="rs_leaders-list">', unsafe_allow_html=True)
            for _, row in top_players_3fg.iterrows():
                player = row['Player']
                team = row.get('Team', '')
                color = team_colors.get(team, '#1e293b')
                
                st.markdown(f"""
                <div class="rs_leader-row">
                    <div class="rs_player-info">
                        <div class="rs_team-indicator" style="background-color: {team_colors.get(team, '#1e293b')};"></div>
                        <span class="rs_player-name">{player}</span>
                    </div>
                    <span class="rs_player-stat">{row["3FGM"]:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Close the game container
        st.markdown('</div>', unsafe_allow_html=True)
        
euroleague_team_colors = {
  'BER': '#ffe14d',  # ALBA Berlin - Softer yellow
  'IST': '#3379bd',  # Anadolu Efes - Softer royal blue
  'MCO': '#d44150',  # Monaco - Softer red
  'BAS': '#3773b3',  # Baskonia - Softer navy blue
  'RED': '#e75a6b',  # Crvena Zvezda - Softer red
  'MIL': '#ff5e75',  # Milan - Softer red with pink tone
  'BAR': '#3674b5',  # Barcelona - Softer deep blue
  'MUN': '#c54960',  # Bayern - Softer burgundy
  'ULK': '#ffd54d',  # Fenerbahce - Softer golden yellow
  'ASV': '#a3a6a9',  # ASVEL - Softer gray
  'TEL': '#ffc966',  # Maccabi - Softer golden orange
  'OLY': '#e66464',  # Olympiacos - Softer red
  'PAN': '#338855',  # Panathinaikos - Softer dark green
  'PRS': '#5d6772',  # Paris - Softer slate
  'PAR': '#4f4d48',  # Partizan - Softer black-gray
  'MAD': '#c0c0c0',  # Real Madrid - Silver instead of white
  'VIR': '#454545',  # Virtus - Softer black
  'ZAL': '#339966',  # Zalgiris - Softer kelly green
}
team_name_short = {
    'BER': 'ALBA BERLIN',
    'IST': 'ANADOLU EFES',
    'MCO': 'AS MONACO', 
    'BAS': 'BASKONIA',
    'RED': 'CRVENA ZVEZDA',
    'MIL': 'OLIMPIA MILANO',
    'BAR': 'FC BARCELONA',
    'MUN': 'BAYERN MUNICH',
    'ULK': 'FENERBAHCE',
    'ASV': 'LDLC ASVEL',
    'TEL': 'MACCABI TEL AVIV',
    'OLY': 'OLYMPIACOS',
    'PAN': 'PANATHINAIKOS',
    'PRS': 'PARIS BASKETBALL',
    'PAR': 'PARTIZAN MOZZART',
    'MAD': 'REAL MADRID',
    'VIR': 'VIRTUS BOLOGNA',
    'ZAL': 'ZALGIRIS KAUNAS',
    # EuroCup teams (you may want to add these as well)
    'LIE': 'LIETKABELIS',
    'ARI': 'ARIS MIDEA',
    'BAH': 'BAHCESEHIR',
    'BES': 'BESIKTAS',
    # ... add other EuroCup team short names
}




def render_round_summary_eurocup(
    simulation_results_df_eurocup, 
    eurocup_team_colors, 
    team_name_short_eurocup, 
    league_name='Eurocup'
):
    # CSS for styling - using unique class names to avoid conflicts
    st.markdown("""
    <style>
    /* Round summary specific styles with unique class names */
    .rs_table-container {
        border: 3px !important;
        border-radius: 16px;
        background-color: white;
        margin: -5px -10px 10px -10px;
        box-shadow: 0 0 0 1px rgba(0,0,0,.2);
    }

    .rs_logo-cell {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(100, 100, 100, 3.5);
        margin-bottom: 8px;
    }

    .rs_logo-cell img {
        width: 60px;
        height: 75px;
        object-fit: contain;
    }

    .rs_team-name-box {
        background-color: white;
        border-radius: 8px;
        padding: 6px;
        box-shadow: 0 4px 10px rgba(100, 100, 100, 1.5);
        margin-bottom: 6px;
        width: 100%;
        text-align: center;
    }

    .rs_team-name {
        font-weight: 800;
        font-size: 11px !important;
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
        color: rgba(26, 31, 54, 0.9);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Dark summary stats table style */
    
    .rs_summary-stats table {
        border-collapse: collapse;
        border-radius: 16px;
        overflow: hidden;
        border: 2px solid white !important;
        background-color: #1a1f36;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        width: 100%;
    }
    
    .rs_summary-stats tr {
        background-color: #1a1f36 !important;  /* Force dark background */
    }
    
    .rs_summary-stats td {
        background-color: #1a1f36 !important;  /* Force dark background */
        padding: 6px;
        text-align: center;
        font-size: 20px;
        vertical-align: middle;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .rs_summary-stats th {
        background-color: #1a1f36 !important;  /* Force dark background */
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 10px;
        text-align: center;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        color: #ffffff;
        padding: 3px;
    }
    
    .rs_summary-stats td div {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 0;
        margin: 0;
    }
    
    .rs_summary-stats td img {
        width: 40px;
        height: 40px;
        vertical-align: middle;
    }
    
    .rs_summary-stats td span {
        font-size: 14px;
        font-weight: 600;
        color: #ffffff !important;
        vertical-align: middle;
    }

    /* Enhanced Leaders section styling */
    .rs_leaders-header {
        background: linear-gradient(to right, #1a1f36, #2c3a5a);
        color: white;
        padding: 4px 8px;
        font-weight: 600;
        font-size: 14px;
        text-align: center;
        text-transform: uppercase;
        border-radius: 6px 6px 0 0;
        letter-spacing: 0.5px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .rs_leaders-list {
        background-color: white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-radius: 0 0 6px 6px;
        overflow: hidden;
        border: 1px solid #e8e8e8;

    }
    
    .rs_leader-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 10px;
        border-bottom: 1px solid #f0f0f0;
        align-items: center;
        background-color: white;
        transition: background-color 0.15s ease;
    }
    
    .rs_leader-row:hover {
        background-color: #f8fafe;
    }
    
    .rs_leader-row:last-child {
        border-bottom: none;
    }
    
    .rs_player-info {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .rs_team-indicator {
        width: 3px;
        height: 20px;
        border-radius: 2px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .rs_player-name {
        font-weight: 500;
        font-size: 12px;
        color: #1a1f36;
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    }
    
    .rs_player-stat {
        font-weight: 700;
        font-size: 14px;
        color: #1a1f36;
        min-width: 30px;
        text-align: right;
        background: linear-gradient(to right, #0d6efd, #3b8ff9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Full-width game info header */
    .rs_game-info-box {
        background-color: white;
        border-radius: 8px;
        padding: 4px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-bottom: 12px;
        margin-top:-15px;
    }
    
    .rs_game-info-icon {
        color: #1a1f36;
        margin-right: 6px;
        font-size: 14px;
    }
    
    .rs_game-info-text {
        font-weight: 600;
        color: #1a1f36;
        font-size: 13px;
    }
    
    /* Filter buttons */
    .rs_filter-buttons {
        display: flex;
        padding: 10px 16px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
        margin-bottom: 10px;
    }
    
    .rs_filter-button {
        background-color: #f1f3f5;
        border: none;
        padding: 6px 14px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 13px;
        color: #495057;
        margin-right: 8px;
    }
    
    .rs_filter-button.active {
        background-color: #1a1f36;
        color: white;
    }

    .rs_game-container {
        margin-bottom: 24px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .rs_versus-symbol {
        display: flex; 
        justify-content: center; 
        align-items: center;
    }

    .rs_versus-box {
        background-color: white; 
        border-radius: 8px; 
        padding: 3px 8px; 
        box-shadow: 0 4px 12px rgba(100, 100, 100, .4);
        margin-top: 30px;
    }

    .rs_versus-text {
        font-size: 16px; 
        color: #1a1f36; 
        font-weight: 800;
    }
    
    /* Game separator */
    .rs_game-separator {
        height: 2px;
        background: linear-gradient(to right, rgba(0,0,0,0.02), rgba(0,0,0,.5), rgba(0,0,0,0.02));
        margin: -15px -15px;
        position: relative;
    }
    
    .rs_game-separator::after {
        content: "";
        position: absolute;
        width: 20px;
        height: 20px;
        background-color: white;
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="%231a1f36"/></svg>');
        background-repeat: no-repeat;
        background-position: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Group games by round
    current_round = simulation_results_df_eurocup['Round'].max()
    round_games = simulation_results_df_eurocup[simulation_results_df_eurocup['Round'] == current_round]

    # Track if we need to add a separator (after the first game)
    first_game = True
    
    # Iterate through each game in the round
    for _, game in round_games.iterrows():
        
        
        home_team = game['Home_Team']
        away_team = game['Away_Team']
        home_code = game['Home_Code']
        away_code = game['Away_Code']
        home_logo = game['Home_Logo']
        away_logo = game['Away_Logo']
        time = game.get('Time', 'N/A')
        arena = game.get('Arena', 'N/A')
        matchup = game['Matchup']
        
        # Get team colors
        home_color = eurocup_team_colors.get(home_code, '#f0f0f0')
        away_color = eurocup_team_colors.get(away_code, '#f0f0f0')

        # Prepare summary stats
        summary_stats_df = pd.DataFrame(game['SimmedTeamStats'][-3:]).T
        summary_stats_df.columns = summary_stats_df.iloc[0]
        summary_stats_df = summary_stats_df.drop(summary_stats_df.index[0])
        summary_stats_df = summary_stats_df.rename(columns={'Total Adjusted': 'Total'})
        summary_stats_df = summary_stats_df[['Spread', 'Total', 'Money']]
        st.markdown('<div class="rs_game-separator"></div>', unsafe_allow_html=True)
        # Game info header using Streamlit columns for 50/50 split
        time_col, arena_col = st.columns(2)
        
        with time_col:
            st.markdown(f"""
            <div class="rs_game-info-box">
                <span class="rs_game-info-icon">🕒</span>
                <span class="rs_game-info-text">{time}</span>
            </div>
            """, unsafe_allow_html=True)
            
        with arena_col:
            st.markdown(f"""
            <div class="rs_game-info-box">
                <span class="rs_game-info-icon">🏟️</span>
                <span class="rs_game-info-text">{arena}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Team logos and summary stats
        logo_col, vs_col, home_logo_col, stats_col = st.columns([1, 0.2, 1, 2.3])
        
        with logo_col:
            st.markdown(
                f"""
                <div class="rs_logo-cell" style="background-color: {eurocup_team_colors.get(away_code, '#f0f0f0')}">
                    <img src="{away_logo}" alt="{away_team} Logo">
                </div>
                <div class="rs_team-name-box">
                    <div class="rs_team-name">{team_name_short_eurocup.get(away_code, away_team)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with vs_col:
            st.markdown("""
            <div class="rs_versus-symbol">
                <div class="rs_versus-box">
                    <span class="rs_versus-text">@</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with home_logo_col:
            st.markdown(
                f"""
                <div class="rs_logo-cell" style="background-color: {eurocup_team_colors.get(home_code, '#f0f0f0')}">
                    <img src="{home_logo}" alt="{home_team} Logo">
                </div>
                <div class="rs_team-name-box">
                    <div class="rs_team-name">{team_name_short_eurocup.get(home_code, home_team)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with stats_col:
            # Creating the dark summary stats table
            html_table = """
            <div class="rs_summary-stats">
                <table>
                    <thead>
                        <tr>
                            <th>TEAM</th>
            """
            for col in summary_stats_df.columns:
                html_table += f"<th>{col.upper()}</th>"
            
            html_table += """
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for idx, row in summary_stats_df.iterrows():
                html_table += "<tr>"

                is_away = idx == away_code or idx == team_name_short.get(away_code, away_team)
                logo_to_use = away_logo if is_away else home_logo
                team_code = away_code if is_away else home_code

                html_table += f'''
                    <td>
                        <div>
                            <img src="{logo_to_use}" alt="{team_code} Logo">
                            <span>{team_code}</span>
                        </div>
                    </td>
                '''

                for col, val in row.items():
                    if isinstance(val, (int, float)):
                        if col == "Money":
                            html_table += f'<td>{val:.2f}</td>'
                        else:
                            html_table += f'<td>{val:.1f}</td>'
                    else:
                        html_table += f"<td>{val}</td>"
                html_table += "</tr>"

            html_table += """
                    </tbody>
                </table>
            </div>
            """

            st.markdown(html_table, unsafe_allow_html=True)
        
        # Get player stats for the matchup
        team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_eurocup()
        filtered_player_statsTeam1 = player_statsTeam1[player_statsTeam1['Matchup'] == matchup]
        filtered_player_statsTeam2 = player_statsTeam2[player_statsTeam2['Matchup'] == matchup]
        
        # Combine player stats from both teams for game-level top 5
        combined_player_stats = pd.concat([filtered_player_statsTeam1, filtered_player_statsTeam2])
        
        # Get top players
        top_players_pts = (
            combined_player_stats.sort_values('PTS', ascending=False)
            .drop_duplicates('Player')
            .head(5)[['Player', 'Team', 'PTS']]
        )
        top_players_reb = (
            combined_player_stats.sort_values('REB', ascending=False)
            .drop_duplicates('Player')
            .head(5)[['Player', 'Team', 'REB']]
        )
        top_players_3fg = (
            combined_player_stats.sort_values('3FGM', ascending=False)
            .drop_duplicates('Player')
            .head(5)[['Player', 'Team', '3FGM']]
        )
        
        # Leaders row with three columns of equal width
        leader_col1, leader_col2, leader_col3 = st.columns(3)
        
        # Points Leaders
        with leader_col1:
            st.markdown('<div class="rs_leaders-header">POINTS LEADERS</div>', unsafe_allow_html=True)
            st.markdown('<div class="rs_leaders-list">', unsafe_allow_html=True)
            for _, row in top_players_pts.iterrows():
                player = row['Player']
                team = row.get('Team', '')
                color = eurocup_team_colors.get(team, '#1e293b')
                
                st.markdown(f"""
                <div class="rs_leader-row">
                    <div class="rs_player-info">
                        <div class="rs_team-indicator" style="background-color: {eurocup_team_colors.get(team, '#1e293b')};"></div>
                        <span class="rs_player-name">{player}</span>
                    </div>
                    <span class="rs_player-stat">{row["PTS"]:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Rebounds Leaders
        with leader_col2:
            st.markdown('<div class="rs_leaders-header">REBOUNDS LEADERS</div>', unsafe_allow_html=True)
            st.markdown('<div class="rs_leaders-list">', unsafe_allow_html=True)
            for _, row in top_players_reb.iterrows():
                player = row['Player']
                team = row.get('Team', '')
                color = eurocup_team_colors.get(team, '#1e293b')
                
                st.markdown(f"""
                <div class="rs_leader-row">
                    <div class="rs_player-info">
                        <div class="rs_team-indicator" style="background-color: {eurocup_team_colors.get(team, '#1e293b')};"></div>
                        <span class="rs_player-name">{player}</span>
                    </div>
                    <span class="rs_player-stat">{row["REB"]:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 3-Pointers Leaders
        with leader_col3:
            st.markdown('<div class="rs_leaders-header">3-POINT LEADERS</div>', unsafe_allow_html=True)
            st.markdown('<div class="rs_leaders-list">', unsafe_allow_html=True)
            for _, row in top_players_3fg.iterrows():
                player = row['Player']
                team = row.get('Team', '')
                color = eurocup_team_colors.get(team, '#1e293b')
                
                st.markdown(f"""
                <div class="rs_leader-row">
                    <div class="rs_player-info">
                        <div class="rs_team-indicator" style="background-color: {eurocup_team_colors.get(team, '#1e293b')};"></div>
                        <span class="rs_player-name">{player}</span>
                    </div>
                    <span class="rs_player-stat">{row["3FGM"]:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Close the game container
        st.markdown('</div>', unsafe_allow_html=True)
        
eurocup_team_colors = {
    'LIE': '#8b1538',  # Lietkabelis
    'ARI': '#ffd700',  # Aris
    'BAH': '#0066b3',  # Bahcesehir
    'BES': '#000000',  # Besiktas
    'BUD': '#003874',  # Buducnost
    'LJU': '#008751',  # Cedevita Olimpija
    'JLB': '#e31837',  # JL Bourg
    'TRE': '#000000',  # Dolomiti Energia Trento
    'CAN': '#fdb927',  # Gran Canaria
    'HJE': '#c8102e',  # Hapoel Jerusalem
    'HTA': '#ec1c24',  # Hapoel Tel Aviv
    'JOV': '#006241',  # Joventut
    'ULM': '#f47920',  # Ulm
    'SOP': '#ffd700',  # Sopot
    'TTK': '#00b4e3',  # Turk Telekom
    'CLU': '#000000',  # Cluj
    'VNC': '#7b2132',  # Venice
    'PAM': '#f47a38',  # Valencia
    'VEO': '#000000',  # Hamburg
    'WOL': '#00a79d'   # Wolves
}

# Light version of team colors
eurocup_team_colors_light = {
    'LIE': '#ffd6e0',  # Light Burgundy (darker)
    'ARI': '#ffe4b3',  # Light Yellow (darker)
    'BAH': '#cce6ff',  # Light Blue (darker)
    'BES': '#e6e6e6',  # Light Gray (darker)
    'BUD': '#cce0ff',  # Light Navy (darker)
    'LJU': '#ccffe0',  # Light Green (darker)
    'JLB': '#ffd0d6',  # Light Red (darker)
    'TRE': '#e6e6e6',  # Light Gray (darker)
    'CAN': '#ffe4b3',  # Light Yellow (darker)
    'HJE': '#ffd0d4',  # Light Red (darker)
    'HTA': '#ffd0d2',  # Light Red (darker)
    'JOV': '#ccffe0',  # Light Green (darker)
    'ULM': '#ffe0cc',  # Light Orange (darker)
    'SOP': '#ffe4b3',  # Light Yellow (darker)
    'TTK': '#ccf2ff',  # Light Blue (darker)
    'CLU': '#e6e6e6',  # Light Gray (darker)
    'VNC': '#ffd6e0',  # Light Burgundy (darker)
    'PAM': '#ffe0cc',  # Light Orange (darker)
    'VEO': '#e6e6e6',  # Light Gray (darker)
    'WOL': '#ccfff8'   # Light Turquoise (darker)
}

# Short team names
team_name_short_eurocup = {
    'LIE': 'LIETKABELIS',
    'ARI': 'ARIS MIDEA',
    'BAH': 'BAHCESEHIR',
    'BES': 'BESIKTAS',
    'BUD': 'BUDUCNOST',
    'LJU': 'CEDEVITA',
    'JLB': 'JL BOURG',
    'TRE': 'DOLOMITI',
    'CAN': 'GRAN CANARIA',
    'HJE': 'HAPOEL BANK',
    'HTA': 'HAPOEL TEL AVIV',
    'JOV': 'JOVENTUT',
    'ULM': 'RATIOPHARM',
    'SOP': 'TREFL SOPOT',
    'TTK': 'TURK TELEKOM',
    'CLU': 'U-BT CLUJ',
    'VNC': 'REYER VENICE',
    'VAL': 'VALENCIA',
    'VEO': 'VEOLIA TOWERS',
    'WOL': 'WOLVES'
}









def main():
    st.set_page_config(layout="wide", page_icon="🏀", page_title="Eurolytics: Euroleague and Eurocup Basketball Simulator")
    
    st.markdown("""
    <style>
        /* Target the main app container */
        [data-testid="stAppViewContainer"] {
    max-width: 950px !important;
    min-width: 950px !important;
    background: #f0f0f0 !important;
    padding: .5rem !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    margin: 0 auto !important;
    margin-top: -145px !important; /* Adjusted from -60px */
}

        /* Reset the default container padding */
        .main .block-container {
            padding: 2rem !important;
            max-width: 100% !important;
            background: #0000ff !important;
        }

        /* Custom background for the space outside the container */
        .stApp {
            background: #7BAFD4 !important;
        }

        /* Ensure elements stay within width */
        /* Adjust the tab list margin and add padding */
/* General Tab Styling */
[data-baseweb="tab-list"] {
    background: white !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    border-radius: 8px !important;
    display: flex !important;
    align-items: center !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    margin-left: -75px !important; /* Reduced left margin */
    margin-top:-10px !important;
    padding: 0px !important;
    height: 28px !important;
    gap: 0px !important; /* Minimal gap between tabs */
}

[data-baseweb="tab-list"] [role="tab"] {
    transition: all 0.2s ease-out !important;
    text-align: center !important;
    border-radius: 6px !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    font-size: 12px !important;
    font-weight: 900 !important;
    padding: 2px 10px !important; /* Reduced horizontal padding */
    margin: 0 !important; /* Removed margins between tabs */
    color: #6b7280 !important;
    background: transparent !important;
    height: 26px !important;
    line-height: 26px !important;
    letter-spacing: 0.4px !important;
    text-transform: uppercase !important;
}

/* Active and Hover States */
[data-baseweb="tab-list"] [role="tab"][aria-selected="true"] {
    color: #1f2937 !important;
    background: rgba(59, 130, 246, 0.2) !important;
    font-weight: 900 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
}

[data-baseweb="tab-list"] [role="tab"]:hover:not([aria-selected="true"]) {
    background: rgba(59, 130, 246, 0.04) !important;
    color: #1f2937 !important;
}

/* Smooth Transitions */
[role="tab"] {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Container Adjustments */
.stTabs {
    margin-left: 0 !important;

    padding-left: 0 !important;
}
        /* Fix select box width */
        [data-testid="stSelectbox"] {
            width: 440px !important;
        }

        /* Adjust column containers */
        [data-testid="column"] {
            padding: 0 !important;
        }

        /* Team stats container */
        .team-stats-euroleague-container {
            width: 250px !important;
            margin: 0 !important;
        }
/* Team stats container */
        .team-stats-eurocup-container {
            width: 250px !important;
            margin: 0 !important;
        }

        /* Logo sizing */
        .logo-cell img {
            max-width: 100px !important;
            height: 100px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Reduce height of the top section/header */
    [data-testid="stHeader"] {
        height: 2.75rem !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        background-color: white;
    }

    .logo-text {
        position: fixed;
        top: 0.5rem;
        left: 24px;
        font-family: "SF Pro Display", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        font-size: 18px;
        letter-spacing: 1.5px;
        color: #1a1f36;
        z-index: 999999;
    }

    [data-testid="stDecoration"] {
        height: 2.75rem !important;
    }

    [data-testid="stAppViewContainer"] {
        padding-top: 2rem !important;
    }

    section[data-testid="stSidebar"] {
        top: 2rem !important;
    }
    </style>

    <div class="logo-text">EUROLYTICS :<span style="font-size: 13px; letter-spacing: normal;">    EUROLEAGUE & EUROCUP BASKETBALL SIMULATOR</span></div>
    """, unsafe_allow_html=True)
    
    # Add JavaScript for tab dropdown behavior
    st.markdown("""
    <script>
document.addEventListener('DOMContentLoaded', function() {
    // Wait for Streamlit to fully render the UI
    setTimeout(function() {
        // Add CSS for improved tab styling
        const style = document.createElement('style');
        style.textContent = `
            /* Override default tab styling */
            [data-baseweb="tab-list"] {
                position: relative !important;
            }
            
            /* Primary top-level tabs (Euroleague, EuroCup) */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-list"]:first-of-type {
                background: linear-gradient(90deg, #1a1f36, #2a344e) !important;
                margin-bottom: 10px !important;
                border-radius: 8px !important; 
                padding: 3px !important;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
                height: 45px !important;
                z-index: 100 !important;
            }
            
            /* Primary tab buttons */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-list"]:first-of-type [role="tab"] {
                color: white !important;
                font-weight: 700 !important;
                font-size: 14px !important;
                padding: 8px 20px !important;
                transition: all 0.2s ease !important;
                border-bottom: 3px solid transparent !important;
                height: 100% !important;
                display: flex !important;
                align-items: center !important;
            }
            
            /* Primary tab hover */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-list"]:first-of-type [role="tab"]:hover {
                background: rgba(255, 255, 255, 0.1) !important;
            }
            
            /* Primary tab active */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-list"]:first-of-type [role="tab"][aria-selected="true"] {
                background: rgba(255, 255, 255, 0.15) !important;
                border-bottom: 3px solid #ff0000 !important;
                color: white !important;
                font-weight: 700 !important;
            }
            
            /* Primary tab active dropdown indicator */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-list"]:first-of-type [role="tab"][aria-selected="true"]::after {
                content: "";
                position: absolute;
                bottom: -10px;
                left: 50%;
                margin-left: -8px;
                width: 0;
                height: 0;
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
                border-top: 8px solid #2a344e;
                z-index: 101;
            }
            
            /* Secondary tabs row (Round X) */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"]:first-of-type {
                background: #f0f2f5 !important;
                border-radius: 8px !important;
                margin-top: 0 !important;
                padding: 3px !important;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
                height: 34px !important;
                margin-left: 20px !important;
                width: auto !important;
                animation: fadeIn 0.3s ease-out;
            }
            
            /* Secondary tab buttons */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"]:first-of-type [role="tab"] {
                color: #444 !important;
                font-weight: 600 !important;
                font-size: 13px !important;
                padding: 4px 14px !important;
                border-radius: 4px !important;
                transition: all 0.2s ease !important;
                border-bottom: 3px solid transparent !important;
                height: 100% !important;
                display: flex !important;
                align-items: center !important;
            }
            
            /* Tertiary tabs (Fixtures, Summary, Leaders) */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"] {
                background: white !important;
                border-radius: 8px !important;
                margin-left: 40px !important;
                padding: 3px !important;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
                height: 30px !important;
                border: 1px solid #eaecef !important;
                animation: fadeIn 0.3s ease-out;
            }
            
            /* Tertiary tab buttons */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"] [role="tab"] {
                color: #555 !important;
                font-weight: 600 !important;
                font-size: 12px !important;
                padding: 4px 12px !important;
                border-radius: 4px !important;
                transition: all 0.2s ease !important;
                height: 100% !important;
                display: flex !important;
                align-items: center !important;
                border-bottom: 2px solid transparent !important;
            }
            
            /* Tertiary tab hover */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"] [role="tab"]:hover {
                background: rgba(0, 0, 0, 0.03) !important;
            }
            
            /* Tertiary tab active */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"] [role="tab"][aria-selected="true"] {
                background: white !important;
                color: #3b82f6 !important;
                border-bottom: 2px solid #3b82f6 !important;
                font-weight: 700 !important;
            }
            
            /* Animation keyframes */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-5px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Animation for tab panels */
            div[data-baseweb="tab-panel"] {
                animation: fadeIn 0.3s ease-out;
            }
            
            /* Fix secondary tab round number */
            div[data-testid="stVerticalBlock"] div[data-baseweb="tab-panel"] div[data-baseweb="tab-list"]:first-of-type [role="tab"]::before {
                content: "ROUND ";
                font-weight: 700;
            }
        `;
        
        document.head.appendChild(style);
        
        // Add a subtle animation when tabs are clicked
        const tabButtons = document.querySelectorAll('[role="tab"]');
        tabButtons.forEach(tab => {
            tab.addEventListener('click', function() {
                // Add a subtle animation class
                tab.classList.add('tab-click-effect');
                
                // Remove it after animation completes
                setTimeout(() => {
                    tab.classList.remove('tab-click-effect');
                }, 300);
            });
        });
        
        // Add animation styles
        const animationStyle = document.createElement('style');
        animationStyle.textContent = `
            .tab-click-effect {
                animation: tabClick 0.3s ease-out;
            }
            
            @keyframes tabClick {
                0% { transform: scale(1); }
                50% { transform: scale(0.97); }
                100% { transform: scale(1); }
            }
        `;
        document.head.appendChild(animationStyle);
        
    }, 1500); // Give more time for UI to render
});
</script>
    """, unsafe_allow_html=True)

    # Start fixed-width container
    st.markdown('<div class="fixed-width-container">', unsafe_allow_html=True)

    # Load data for Round 29
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pickle_path = os.path.join(script_dir, 'data', 'euroleague_simulations_round_33.pkl')
    with open(pickle_path, 'rb') as f:
        simulation_results_df = pickle.load(f)
    
    # Load data for Round 30
    pickle_path_round_33 = os.path.join(script_dir, 'data', 'euroleague_simulations_round_33.pkl')
    with open(pickle_path_round_33, 'rb') as f:
        simulation_results_df_round_33 = pickle.load(f)
        
    # Load data for Round 31
    pickle_path_round_34 = os.path.join(script_dir, 'data', 'euroleague_simulations_round_34.pkl')
    with open(pickle_path_round_34, 'rb') as f:
        simulation_results_df_round_34 = pickle.load(f)

    st.markdown("""
       <style>
    .summary-stats-euroleague table,
    .summary-stats-eurocup table {

        border-collapse: collapse;
        border-radius: 16px;
        overflow: hidden;
        border: 2px solid white !important;
        margin-top: -15px;
        background-color: #1a1f36;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }

    .summary-stats-euroleague tr,
    .summary-stats-eurocup tr {
        background-color: #1a1f36 !important;  /* Force dark background */
    }

    .summary-stats-euroleague td,
    .summary-stats-eurocup td {
        background-color: #1a1f36 !important;  /* Force dark background */
        padding: 8px;
        text-align: center;
        font-size:20px;
        vertical-align: middle;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .summary-stats-euroleague th,
    .summary-stats-eurocup th {
        background-color: #1a1f36 !important;  /* Force dark background */
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 10px;
        text-align: center;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        color: #ffffff;
    }

    /* Keep other styles the same */
    .summary-stats-euroleague td div,
    .summary-stats-eurocup td div {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 0;
        margin: 0;
    }

    .summary-stats-euroleague td img,
    .summary-stats-eurocup td img {
        width: 40px;
        height: 40px;
        vertical-align: middle;
    }

    .summary-stats-euroleague td span,
    .summary-stats-eurocup td span {
        font-size: 14px;
        font-weight: 600;
        color: #ffffff !important;
        vertical-align: middle;
    }
    
 
.stSelectbox > div[data-baseweb="select"] > div[key="simulate-select-matchup"] > div,
div[data-baseweb="select"] {
    margin-top: -38px;
    margin-left: -55px;
    font-weight: 700;
    border: 3px solid #A5B4FC !important;
    border-radius: 10px;
    padding: 3px 8px;
    height: 32px;
    min-height: 32px !important;
    background-color: rgb(245, 247, 255) !important; /* Soft, light blue background */
    color: rgb(59, 130, 246); /* More vibrant blue text */
    font-size: 12px;
    transition: all 0.2s ease-in-out;
    box-shadow: 0px 1px 4px rgba(45, 99, 226, 0.2);
    display: flex;
    align-items: center;
}

/* Target the inner select button */
.stSelectbox > div[data-baseweb="select"] > div {
    height: 22px !important;
    min-height: 22px !important;
    display: flex;
    align-items: center;
}

/* Target the value container */
.stSelectbox [data-baseweb="select"] [data-testid="stMarkdownContainer"] {
    line-height: 1.1;
    padding-top: 0;
    padding-bottom: 0;
    display: flex;
    align-items: center;
    font-size: 14px;
}

/* Hover Effect */
div[data-baseweb="select"]:hover {
    border-color: #A5B4FC !important; /* Soft indigo border on hover */
    background-color: #EEF2FF !important; /* Lighter blue background on hover */
}

button:hover, 
input:hover, 
select:hover, 
div[data-baseweb="select"]:hover, 
.stButton > button:hover, 
.stSelectbox > div > div[data-baseweb="select"]:hover {
    border-color: #A5B4FC !important;
    background-color: #EEF2FF !important;
    transition: all 0.2s ease;
}

/* Focus Effect */
div[data-baseweb="select"]:focus-within {
    border-color: #6366F1 !important;
    box-shadow: 0 0 8px rgba(99, 102, 241, 0.3);
}


/* Dropdown Menu Styling */
div[data-baseweb="popover"] {
    border-radius: 10px;
    border: 1px solid #E5E7EB;
    background-color: #FFFFFF;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
}

/* Dropdown Item - Smaller Font */
div[data-baseweb="option"] {
    padding: 8px 12px; /* Slightly reduced padding */
    font-size: 10px !important; /* Smaller font size */
    color: #1F2937; /* Darker text color */
    transition: background-color 0.2s ease-in-out;
}

/* Hover effect for dropdown item */
div[data-baseweb="option"]:hover {
    background-color: #F3F4F6;
}

div[data-baseweb="select"]:hover {
    box-shadow: 0 4px 12px rgba(45, 99, 226, 0.2);
}    
.rs_game-separator3 {
        height: 2px;
        background: linear-gradient(to right, rgba(0,0,0,0.02), rgba(0,0,0,.5), rgba(0,0,0,0.02));
        margin: 1px 0px -15px 0px !important;
        position: relative;
    }
    
    .rs_game-separator3::after {
        content: "";
        position: absolute;
        width: 20px;
        height: 20px;
        background-color: white;
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="%231a1f36"/></svg>');
        background-repeat: no-repeat;
        background-position: center;
    }


       </style>
   """, unsafe_allow_html=True)

    # Load team stats data
    team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_euroleague()
    if 'team_stats' not in st.session_state:
        st.session_state['team_stats'] = team_stats
    if 'player_statsTeam1' not in st.session_state:
        st.session_state['player_statsTeam1'] = player_statsTeam1
    if 'player_statsTeam2' not in st.session_state:
        st.session_state['player_statsTeam2'] = player_statsTeam2

    matchups = team_stats['Matchup'].unique().tolist()
    
    if 'simulation_results_df' not in st.session_state:
        st.session_state['simulation_results_df'] = simulation_results_df
        
    # Store Round 30 and 31 data in session state
    if 'simulation_results_df_round_30' not in st.session_state:
        st.session_state['simulation_results_df_round_33'] = simulation_results_df_round_33
        
    if 'simulation_results_df_round_31' not in st.session_state:
        st.session_state['simulation_results_df_round_34'] = simulation_results_df_round_34
    
    # Load EuroCup simulation results
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pickle_path_eurocup = os.path.join(script_dir, 'data', 'eurocup_simulations_semifinals_game_3.pkl')
    with open(pickle_path_eurocup, 'rb') as f:
        simulation_results_df_eurocup = pickle.load(f)
    
    # Load EuroCup team stats
    team_stats_eurocup, player_statsTeam1_eurocup, player_statsTeam2_eurocup = create_sample_data_eurocup()
    if 'team_stats_eurocup' not in st.session_state:
        st.session_state['team_stats_eurocup'] = team_stats_eurocup
    if 'player_statsTeam1_eurocup' not in st.session_state:
        st.session_state['player_statsTeam1_eurocup'] = player_statsTeam1_eurocup
    if 'player_statsTeam2_eurocup' not in st.session_state:
        st.session_state['player_statsTeam2_eurocup'] = player_statsTeam2_eurocup
    
    if 'simulation_results_df_eurocup' not in st.session_state:
        st.session_state['simulation_results_df_eurocup'] = simulation_results_df_eurocup
        
    # Get EuroCup matchups
    matchups_eurocup = team_stats_eurocup['Matchup'].unique().tolist()
    
    # Top level tabs: Euroleague and EuroCup
    sport_tabs = st.tabs(["Euroleague", "EuroCup", "About"])
    


# EUROLEAGUE TAB
    with sport_tabs[0]:
        # Get the current round for Euroleague
        current_round_euroleague = simulation_results_df['Round'].max()
        
        # Parse the round string: "Regular Season Round 27"
        # Split into parts and extract what we need
        round_parts = current_round_euroleague.split('Round')
        season_name = round_parts[0].strip()  # "Regular Season"
        round_number = int(round_parts[1].strip())  # 29
        
        # Create tabs for season name and rounds separately
        # Use bold font for the season name tab
        euroleague_round_tab_labels = [
            f"****{season_name}****",
            f"Round {round_number}",
            f"Round {round_number + 1}",
  #          f"Round {round_number + 2}"
        ]
        euroleague_round_tabs = st.tabs(euroleague_round_tab_labels)

        # Define a function to create the round content for any dataset
        def create_round_content(simulation_data, tab_suffix=""):
    # Generate player stats for this round
            team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_euroleague(simulation_data)
    
    # Create the third level tabs (Fixtures, Summary, Leaders)
            euroleague_section_tabs = st.tabs(["Fixtures", "Summary", "Leaders"])
            
            # Fixtures Summary tab (Summary)
            with euroleague_section_tabs[1]:
                render_round_summary(
                    simulation_data, 
                    euroleague_team_colors, 
                    team_name_short, 
                    'Euroleague'
                )
            
            # Fixtures tab (Fixtures)
            with euroleague_section_tabs[0]:
                st.markdown('<div class="rs_game-separator3"></div>', unsafe_allow_html=True)

                # Add some spacing
                st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)

                col1, col2 = st.columns([1,.82])
                
                # Get matchups specific to this round's dataset
                round_matchups = simulation_data['Matchup'].unique().tolist()
                
                with col1:
                    selected_matchup = st.selectbox(
                        'Select Matchup',
                        round_matchups,
                        key=f'simulate_matchup_select{tab_suffix}',
                        label_visibility='hidden'
                    )
                
                with col2:
                    matchup_data = simulation_data[simulation_data['Matchup'] == selected_matchup].iloc[0]
                    time_value = matchup_data.get('Time', 'N/A')
                    arena_value = matchup_data.get('Arena', 'N/A')
                    
                    st.markdown(
                        f"""
                        <div style="
                            background-color: white; 
                            -webkit-background-color: white;
                            background: white;
                            -webkit-background: white;
                            border-radius: 8px; 
                            padding: 5px 8px; 
                            margin-top: -10px; 
                            box-shadow: 0 4px 6px rgba(100, 100, 100, 0.4);
                            margin-right:-50px; 
                            margin-left:-27px;
                            display: flex; 
                            justify-content: center; 
                            align-items: center; 
                            gap: 30px; 
                            color: black !important;">
                            <div style="
                                text-align: center; 
                                font-weight: 700;  
                                font-size: 12px; 
                                color: rgb(26, 31, 54);">{time_value}</div>
                            <div style="
                                text-align: center; 
                                font-weight: 700;  
                                font-size: 12px; 
                                color: rgb(26, 31, 54);">{arena_value}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Store the current data in session state temporarily for the render function
                temp_current_data = st.session_state.get('simulation_results_df')
                st.session_state['simulation_results_df'] = simulation_data
                
                render_stats_tables_euroleague(selected_matchup, round_matchups, f"simulate{tab_suffix}")
                
                # Restore original data
                st.session_state['simulation_results_df'] = temp_current_data
            
            # Statistics tab
            with euroleague_section_tabs[2]:
                # Add custom styling with white background and updated layout
                st.markdown("""
                <style>
                /* Game separator styling */
                .rs_game-separator {
                    height: 2px;
                    background: linear-gradient(to right, rgba(0,0,0,0.02), rgba(0,0,0,.5), rgba(0,0,0,0.02));
                    margin: 5px -15px 15px -15px;
                    position: relative;
                }
                
                .rs_game-separator::after {
                    content: "";
                    position: absolute;
                    width: 20px;
                    height: 20px;
                    background-color: white;
                    border-radius: 50%;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="%231a1f36"/></svg>');
                    background-repeat: no-repeat;
                    background-position: center;
                }
                
                /* Table header styling with title - unique for round leaders */
                .rl_leaders_table_header {
                    background-color: #1a1f36;
                    color: white;
                    padding: 6px 8px;
                    font-weight: 600;
                    text-align: center;
                    font-size: 12px;
                    letter-spacing: 0.5px;
                    border-radius: 8px 8px 0 0;
                    font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
                    text-transform: uppercase;
                    position: relative;
                    z-index: 10;
                }
                
                /* Table rows styling with unique names */
                .rl_leader_row {
                    display: grid;
                    grid-template-columns: 60px 1fr 100px;
                    padding: 6px 10px;
                    align-items: center;
                    border-bottom: 1px solid #f0f2f5;
                    background-color: white;
                }
                
                .rl_leader_row:last-child {
                    border-bottom: none;
                }
                
                .rl_leader_row:hover {
                    background-color: #f8f9fa;
                }
                
                /* Rank cell styling */
                .rl_rank_cell {
                    text-align: center;
                    font-weight: 700;
                    font-size: 16px;
                    color: #64748b;
                }
                
                /* Player cell styling */
                .rl_player_cell {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }
                
                .rl_team_logo {
                    width: 24px;
                    height: 24px;
                    object-fit: contain;
                }
                
                .rl_player_name {
                    font-weight: 700;
                    font-size: 15px;
                    color: #1a1f36;
                }
                
                .rl_player_team {
                    font-size: 12px;
                    color: #64748b;
                    font-weight: 400;
                }
                
                /* Stat cell styling */
                .rl_stat_cell {
                    text-align: right;
                    font-weight: 700;
                    font-size: 16px;
                    color: #3b82f6;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Add game separator
                st.markdown('<div class="rs_game-separator"></div>', unsafe_allow_html=True)
                
                # Get current round
                current_round = simulation_data['Round'].max()
                round_games = simulation_data[simulation_data['Round'] == current_round]
                
                # Create empty DataFrame to store all player stats for the round
                all_player_stats = pd.DataFrame()
                
                # Define logo mappings for teams
                team_logos = {}
                
                # Iterate through each game to get player stats and combine them
                for _, game in round_games.iterrows():
                        matchup = game['Matchup']

                        team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_euroleague(simulation_data)
                        filtered_player_statsTeam1 = player_statsTeam1[player_statsTeam1['Matchup'] == matchup].copy()
                        filtered_player_statsTeam2 = player_statsTeam2[player_statsTeam2['Matchup'] == matchup].copy()
                        
                        # Add matchup information
                        filtered_player_statsTeam1['Matchup'] = matchup
                        filtered_player_statsTeam2['Matchup'] = matchup
                        
                        # Combine stats from both teams
                        game_stats = pd.concat([filtered_player_statsTeam1, filtered_player_statsTeam2])
                        
                        # Add to the combined dataframe
                        all_player_stats = pd.concat([all_player_stats, game_stats])
                        
                        # Store team logos
                        team_logos[game['Home_Code']] = game['Home_Logo']
                        team_logos[game['Away_Code']] = game['Away_Logo']
                
                # Define stat options with labels and corresponding column names
                stat_options = {
                    "Points": "PTS",
                    "Offensive Rebounds": "OREB",
                    "Defensive Rebounds": "DREB",
                    "Total Rebounds": "REB", 
                    "Turnovers": "TO",
                    "2-Point Field Goals": "2FGM",
                    "2-Point Attempts": "2FGA",
                    "2-Point %": "2PT%",
                    "3-Point Field Goals": "3FGM",
                    "3-Point Attempts": "3FGA",
                    "3-Point %": "3PT%",
                    "Free Throws": "FT",
                    "Free Throw Attempts": "FTA",
                    "Free Throw %": "FT%",
                    "Minutes": "MIN",
                }
                
                # Use columns to position the selectbox on the right
                label_col, select_col = st.columns([1, 3])

                with label_col:
                    st.markdown('<div style="padding-top: 5px; font-weight: 700; font-family: -apple-system, system-ui, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif; text-transform: uppercase; margin-top: -12px;margin-left:-30px; color: #1a1f36; letter-spacing: 0.1px; display: flex; align-items: center;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; color: #3b82f6;"><path d="M11 3L11 21M3 12L21 12"></path></svg>Select Statistic:</div>', unsafe_allow_html=True)

                with select_col:
                    # Add the selectbox
                    stat_label = st.selectbox(
                        "",
                        options=list(stat_options.keys()),
                        index=0,
                        key=f"rl_stat_selector{tab_suffix}",
                        label_visibility="hidden"
                    )
                
                # Get the selected stat column name
                selected_stat = stat_options[stat_label]
                
                # Sort and get top players
                top_players = all_player_stats.sort_values(selected_stat, ascending=False)
                
                # Drop duplicates to get unique players and take top 20
                top_players = top_players.drop_duplicates("Player")
                
                # Add title as table header with unique class name
                st.markdown(f'''
                <div class="rl_leaders_table_header" style="display: flex; justify-content: space-between;">
                    <div>{current_round_euroleague}</div>
                    <div>{stat_label} LEADERS</div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Generate table rows with unique class names - Generate only once
                for i, (idx, row) in enumerate(top_players.iterrows()):
                    player = row['Player']
                    team = row.get('Team', '')
                    matchup = row.get('Matchup', '')
                    
                    # Get team logo
                    logo_url = team_logos.get(team, '')
                    if not logo_url:
                        # If logo not found, use a placeholder
                        logo_url = "https://via.placeholder.com/32"
                    
                    # Format stat value based on type
                    if selected_stat.endswith("%"):
                        stat_value = f"{row[selected_stat]:.2f}%"
                    else:
                        stat_value = f"{row[selected_stat]:.1f}"
                    
                    # Create row with game name on same line - using unique class names
                    st.markdown(f"""
                    <div class="rl_leader_row">
                        <div class="rl_rank_cell">{i+1}</div>
                        <div class="rl_player_cell">
                            <img src="{logo_url}" class="rl_team_logo" alt="{team}">
                            <div>
                                <span class="rl_player_name">{player}</span> <span class="rl_player_team">{matchup}</span>
                            </div>
                        </div>
                        <div class="rl_stat_cell">{stat_value}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Close table container
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Season Name tab - use the same content as the current round tab
        with euroleague_round_tabs[0]:
            # Call the same function to create identical content with a unique suffix
            create_round_content(simulation_results_df, "_season_tab")
            
        # Inside the current Round tab 
        with euroleague_round_tabs[1]:
            # Call the function to create the content with a different suffix
            create_round_content(simulation_results_df, "_round_33_tab")
        
        # Round +1 tab
        with euroleague_round_tabs[2]:
            create_round_content(simulation_results_df_round_34, "_round_34_tab")
            
        # Round +2 tab
    #    with euroleague_round_tabs[3]:
  #          create_round_content(simulation_results_df_round_34, "_round_34_tab")

    # EUROCUP TAB
    with sport_tabs[1]:
        # Get the current round for EuroCup
        current_round_eurocup = simulation_results_df_eurocup['Round'].max()
        
        # Create round tabs - NEW LAYER OF TABS
        eurocup_round_tab_labels = [f"****Playoffs**** {current_round_eurocup}"]
        eurocup_round_tabs = st.tabs(eurocup_round_tab_labels)
        
        # Inside the Round tab
        with eurocup_round_tabs[0]:
            # Create the third level tabs (Fixtures, Summary, Leaders)
            eurocup_section_tabs = st.tabs(["Fixtures", "Summary", "Leaders"])
            
            # Fixtures Summary tab
            with eurocup_section_tabs[1]:
                render_round_summary_eurocup(
                    simulation_results_df_eurocup, 
                    eurocup_team_colors, 
                    team_name_short_eurocup, 
                    'Eurocup'
                )
            
            # Fixtures tab
            with eurocup_section_tabs[0]:
                st.markdown('<div class="rs_game-separator3"></div>', unsafe_allow_html=True)

                # Add some spacing
                st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
                col1, col2 = st.columns([1,.82])
                
                with col1:
                    selected_matchup_eurocup = st.selectbox(
                        'Select Matchup',
                        matchups_eurocup,
                        key='simulate_matchup_select_eurocup',
                        label_visibility='hidden'
                    )
                
                with col2:
                    matchup_data_eurocup = simulation_results_df_eurocup[simulation_results_df_eurocup['Matchup'] == selected_matchup_eurocup].iloc[0]
                    time_value_eurocup = matchup_data_eurocup.get('Time', 'N/A')
                    arena_value_eurocup = matchup_data_eurocup.get('Arena', 'N/A')
                    
                    st.markdown(
                        f"""
                        <div style="
                            background-color: white; 
                            -webkit-background-color: white;
                            background: white;
                            -webkit-background: white;
                            border-radius: 8px; 
                            padding: 5px 8px; 
                            margin-top: -10px; 
                            box-shadow: 0 4px 6px rgba(100, 100, 100, 0.4);
                            margin-right:-50px; 
                            margin-left:-27px;
                            display: flex; 
                            justify-content: center; 
                            align-items: center; 
                            gap: 30px; 
                            color: black !important;">
                            <div style="
                                text-align: center; 
                                font-weight: 700;  
                                font-size: 12px; 
                                color: rgb(26, 31, 54);">{time_value_eurocup}</div>
                            <div style="
                                text-align: center; 
                                font-weight: 700;  
                                font-size: 12px; 
                                color: rgb(26, 31, 54);">{arena_value_eurocup}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                render_stats_tables_eurocup(selected_matchup_eurocup, matchups_eurocup, simulation_results_df_eurocup, "simulate")
            
            # Statistics tab
            with eurocup_section_tabs[2]:
                # Add custom styling with white background and updated layout
                st.markdown("""
                <style>
                /* Game separator styling */
                .rs_game-separator2 {
                    height: 2px;
                    background: linear-gradient(to right, rgba(0,0,0,0.02), rgba(0,0,0,.5), rgba(0,0,0,0.02));
                    margin: -15px -15px 15px -15px;
                    position: relative;
                }
                
                .rs_game-separator2::after {
                    content: "";
                    position: absolute;
                    width: 20px;
                    height: 20px;
                    background-color: white;
                    border-radius: 50%;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="%231a1f36"/></svg>');
                    background-repeat: no-repeat;
                    background-position: center;
                }
                
                /* Table header styling with title - unique for round leaders */
                .rl_leaders_table_header {
                    background-color: #1a1f36;
                    color: white;
                    padding: 6px 8px;
                    font-weight: 600;
                    text-align: center;
                    font-size: 12px;
                    letter-spacing: 0.5px;
                    border-radius: 8px 8px 0 0;
                    font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
                    text-transform: uppercase;
                    position: relative;
                    z-index: 10;
                }
                
                /* Table rows styling with unique names */
                .rl_leader_row {
                    display: grid;
                    grid-template-columns: 60px 1fr 100px;
                    padding: 6px 10px;
                    align-items: center;
                    border-bottom: 1px solid #f0f2f5;
                    background-color: white;
                }
                
                .rl_leader_row:last-child {
                    border-bottom: none;
                }
                
                .rl_leader_row:hover {
                    background-color: #f8f9fa;
                }
                
                /* Rank cell styling */
                .rl_rank_cell {
                    text-align: center;
                    font-weight: 700;
                    font-size: 16px;
                    color: #64748b;
                }
                
                /* Player cell styling */
                .rl_player_cell {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }
                
                .rl_team_logo {
                    width: 24px;
                    height: 24px;
                    object-fit: contain;
                }
                
                .rl_player_name {
                    font-weight: 700;
                    font-size: 15px;
                    color: #1a1f36;
                }
                
                .rl_player_team {
                    font-size: 12px;
                    color: #64748b;
                    font-weight: 400;
                }
                
                /* Stat cell styling */
                .rl_stat_cell {
                    text-align: right;
                    font-weight: 700;
                    font-size: 16px;
                    color: #3b82f6;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Add game separator
                st.markdown('<div class="rs_game-separator2"></div>', unsafe_allow_html=True)
                
                # Get current round
                current_round = simulation_results_df_eurocup['Round'].max()
                round_games = simulation_results_df_eurocup[simulation_results_df_eurocup['Round'] == current_round]
                
                # Create empty DataFrame to store all player stats for the round
                all_player_stats = pd.DataFrame()
                
                # Define logo mappings for teams
                team_logos = {}
                
                # Iterate through each game to get player stats and combine them
                for _, game in round_games.iterrows():
                        matchup = game['Matchup']
                        
                        # Get player stats for the matchup
                        team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_eurocup()
                        filtered_player_statsTeam1 = player_statsTeam1[player_statsTeam1['Matchup'] == matchup].copy()
                        filtered_player_statsTeam2 = player_statsTeam2[player_statsTeam2['Matchup'] == matchup].copy()
                        
                        # Add matchup information
                        filtered_player_statsTeam1['Matchup'] = matchup
                        filtered_player_statsTeam2['Matchup'] = matchup
                        
                        # Combine stats from both teams
                        game_stats = pd.concat([filtered_player_statsTeam1, filtered_player_statsTeam2])
                        
                        # Add to the combined dataframe
                        all_player_stats = pd.concat([all_player_stats, game_stats])
                        
                        # Store team logos
                        team_logos[game['Home_Code']] = game['Home_Logo']
                        team_logos[game['Away_Code']] = game['Away_Logo']
                
                # Define stat options with labels and corresponding column names
                stat_options = {
                    "Points": "PTS",
                    "Offensive Rebounds": "OREB",
                    "Defensive Rebounds": "DREB",
                    "Total Rebounds": "REB", 
                    "Turnovers": "TO",
                    "2-Point Field Goals": "2FGM",
                    "2-Point Attempts": "2FGA",
                    "2-Point %": "2PT%",
                    "3-Point Field Goals": "3FGM",
                    "3-Point Attempts": "3FGA",
                    "3-Point %": "3PT%",
                    "Free Throws": "FT",
                    "Free Throw Attempts": "FTA",
                    "Free Throw %": "FT%",
                    "Minutes": "MIN",
                }
                
                # Use columns to position the selectbox on the right
                label_col, select_col = st.columns([1, 3])

                with label_col:
                    st.markdown('<div style="padding-top: 5px; font-weight: 700; font-family: -apple-system, system-ui, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif; text-transform: uppercase; margin-top: -12px;margin-left:-30px; color: #1a1f36; letter-spacing: 0.1px; display: flex; align-items: center;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; color: #3b82f6;"><path d="M11 3L11 21M3 12L21 12"></path></svg>Select Statistic:</div>', unsafe_allow_html=True)
                with select_col:
                    # Add the selectbox
                    stat_label = st.selectbox(
                        "",
                        options=list(stat_options.keys()),
                        index=0,
                        key="rl_stat_selector2",
                        label_visibility="hidden"
                    )
                
                # Get the selected stat column name
                selected_stat = stat_options[stat_label]
                
                # Sort and get top players
                top_players = all_player_stats.sort_values(selected_stat, ascending=False)
                
                # Drop duplicates to get unique players and take top 20
                top_players = top_players.drop_duplicates("Player")
                
                # Add title as table header with unique class name
                st.markdown(f'''
                <div class="rl_leaders_table_header" style="display: flex; justify-content: space-between;">
                    <div>{simulation_results_df["Round"].max()}</div>
                    <div>{stat_label} LEADERS</div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Generate table rows with unique class names - Generate only once
                for i, (idx, row) in enumerate(top_players.iterrows()):
                    player = row['Player']
                    team = row.get('Team', '')
                    matchup = row.get('Matchup', '')
                    
                    # Get team logo
                    logo_url = team_logos.get(team, '')
                    if not logo_url:
                        # If logo not found, use a placeholder
                        logo_url = "https://via.placeholder.com/32"
                    
                    # Format stat value based on type
                    if selected_stat.endswith("%"):
                        stat_value = f"{row[selected_stat]:.2f}%"
                    else:
                        stat_value = f"{row[selected_stat]:.1f}"
                    
                    # Create row with game name on same line - using unique class names
                    st.markdown(f"""
                    <div class="rl_leader_row">
                        <div class="rl_rank_cell">{i+1}</div>
                        <div class="rl_player_cell">
                            <img src="{logo_url}" class="rl_team_logo" alt="{team}">
                            <div>
                                <span class="rl_player_name">{player}</span> <span class="rl_player_team">{matchup}</span>
                            </div>
                        </div>
                        <div class="rl_stat_cell">{stat_value}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Close table container
                st.markdown('</div>', unsafe_allow_html=True)

    with sport_tabs[2]:
        st.markdown('<div class="about-tab-content">', unsafe_allow_html=True)
        # Add CSS for styling the About tab with enhanced professional appearance
        st.markdown("""
<style>
    body {
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif !important;
    }
    
    .about-header {
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #333 !important;
        margin-bottom: 0px !important;
        margin-top:-15px !important;
        text-align: center !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        background: linear-gradient(to right, #2c3e50, #3498db) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    .section-header {
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #333 !important;
        margin-top: 15px !important;
        margin-bottom: 22px !important;
        padding-left: 18px !important;
        border-left: 4px solid #3b82f6 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        position: relative !important;
        transition: transform 0.3s ease !important;
    }
    
    .section-header:hover {
        transform: translateX(5px) !important;
    }
    
    /* Add a subtle line after the section header */
    .section-header::after {
        content: "" !important;
        position: absolute !important;
        bottom: -10px !important;
        left: 0 !important;
        width: 100% !important;
        height: 1px !important;
        background: linear-gradient(to right, rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0.05)) !important;
    }
    
    .section-text {
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif !important;
        font-size: 16px !important;
        color: #2c3e50 !important;
        margin-bottom: 15px !important;
        line-height: 1.7 !important;
        margin-top: 16px !important;
        font-weight: 400 !important;
        background-color: #f4f6f7 !important;
        padding: 15px 20px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    .bullet-container {
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
        padding: 15px !important;
        background-color: #f9fafb !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03) !important;
        margin-top: 10px !important;
    }
    
    .bullet-point {
        display: flex !important;
        align-items: flex-start !important;
    }
    
    .bullet-marker {
        color: #3b82f6 !important;
        font-size: 18px !important;
        line-height: 1 !important;
        margin-right: 12px !important;
        margin-top: 1px !important;
        font-weight: bold !important;
    }
    
    .bullet-text {
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif !important;
        color: #2c3e50 !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        flex: 1 !important;
    }
    
    .note-text {
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif !important;
        font-style: italic !important;
        color: #6b7280 !important;
        font-size: 14px !important;
        background-color: rgba(59, 130, 246, 0.05) !important;
        padding: 3px 6px !important;
        border-radius: 4px !important;
    }
    
    /* About page separator styling */
    .about-separator {
        height: 2px !important;
        background: linear-gradient(to right, rgba(0,0,0,0.02), rgba(0,0,0,.5), rgba(0,0,0,0.02)) !important;
        margin: -15px -15px 30px -25px !important;
        position: relative !important;
    }
    
    .about-separator::after {
        content: "" !important;
        position: absolute !important;
        width: 20px !important;
        height: 20px !important;
        background-color: white !important;
        border-radius: 50% !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" fill="%231a1f36"/></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
    }
</style>
""", unsafe_allow_html=True)
        
        st.markdown('<div class="sport-about-tab">', unsafe_allow_html=True)
        
        # Add the separator above the title
        st.markdown('<div class="about-separator"></div>', unsafe_allow_html=True)
        
        # Title
        st.markdown('<h1 class="about-header">About the Analytics</h1>', unsafe_allow_html=True)
        
        # Data Collection section
        st.markdown('<h2 class="section-header">Data Collection & Enhancement</h2>', unsafe_allow_html=True)
        
        # Bullet points with proper alignment
        bullet_points = [
            "Utilize the Euroleague API to collect play-by-play, boxscore and shot location data",
            "Identify players on the court at each moment of every game",
            "Find and address inconsistencies in the data to fix actual and potential errors",
            "Break down methods to the start and end of each possession",
            "Eliminate garbage time possessions"
        ]
        
        for point in bullet_points:
            st.markdown(f"""
            <div class="bullet-point">
                <span class="bullet-marker">•</span>
                <span class="bullet-text">{point}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Player Impact Analysis section
        st.markdown('<h2 class="section-header">Player Elo Ratings</h2>', unsafe_allow_html=True)
        
        impact_points = [
	    "Apply a unique weighting system to determine players' impact on each possession",
            "Player Level Datasets to create 20+ Offensive and Defensive Player-level Elo ratings, inclusive of Pace ratings",
        ]
        
        for point in impact_points:
            st.markdown(f"""
            <div class="bullet-point">
                <span class="bullet-marker">•</span>
                <span class="bullet-text">{point}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Advanced Metrics section
        st.markdown('<h2 class="section-header">Game Simulations</h2>', unsafe_allow_html=True)
        
        metrics_points = [
            "Find lineups and apply minutes model to estimate player minutes, with ability to add/remove players at will",
            "Use player elo ratings to derive team transition matrices, simulating games 50,000 times",
            "Apply Home Court Advantage Factor to capture impact across all major statistical categories (shooting percentages, offensive rebounding, fouls, etc.)",
        ]
        
        for point in metrics_points:
            st.markdown(f"""
            <div class="bullet-point">
                <span class="bullet-marker">•</span>
                <span class="bullet-text">{point}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
       
    # Close all divs
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) 

if __name__ == "__main__":
    main()