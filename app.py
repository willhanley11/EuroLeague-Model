import streamlit as st
import pandas as pd
import os
import pickle

def create_sample_data_euroleague():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pickle_path = os.path.join(script_dir, 'data', 'euroleague_simulations.pkl')
    
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

def create_sample_data_eurocup():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pickle_path = os.path.join(script_dir, 'data', 'eurocup_simulations.pkl')
    
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
   'BER': '#ffed99',  # ALBA Berlin - Light yellow
   'IST': '#d6e4ff',  # Anadolu Efes - Light navy 
   'MCO': '#ffd6d9',  # Monaco - Light red
   'BAS': '#d6e4ff',  # Baskonia - Light navy
   'RED': '#ffd6d9',  # Zvezda - Light red
   'MIL': '#ffd6d9',  # Milan - Light red
   'BAR': '#d6e4ff',  # Barcelona - Light blue
   'MUN': '#ffd6d9',  # Bayern - Light red
   'ULK': '#ffed99',  # Fenerbahce - Light yellow
   'ASV': '#e6e6e6',  # ASVEL - Light gray
   'TEL': '#ffed99',  # Maccabi - Light yellow
   'OLY': '#ffd6d9',  # Olympiacos - Light red
   'PAN': '#d6ffe0',  # Panathinaikos - Light green
   'PRS': '#e6e6e6',  # Paris - Light gray
   'PAR': '#e6e6e6',  # Partizan - Light gray
   'MAD': '#d6e4ff',  # Madrid - Light blue
   'VIR': '#e6e6e6',  # Virtus - Light gray
   'ZAL': '#d6ffe0',  # Zalgiris - Light green
}
   euroleague_team_colors_light = {
   'BER': '#fff9e6',  # ALBA Berlin
   'IST': '#f2f5ff',  # Anadolu Efes
   'MCO': '#fff2f3',  # Monaco
   'BAS': '#f2f5ff',  # Baskonia
   'RED': '#fff2f3',  # Zvezda
   'MIL': '#fff2f3',  # Milan 
   'BAR': '#f2f5ff',  # Barcelona
   'MUN': '#fff2f3',  # Bayern
   'ULK': '#fff9e6',  # Fenerbahce
   'ASV': '#f7f7f7',  # ASVEL
   'TEL': '#fff9e6',  # Maccabi
   'OLY': '#fff2f3',  # Olympiacos
   'PAN': '#f2fff5',  # Panathinaikos
   'PRS': '#f7f7f7',  # Paris
   'PAR': '#f7f7f7',  # Partizan
   'MAD': '#f2f5ff',  # Madrid
   'VIR': '#f7f7f7',  # Virtus
   'ZAL': '#f2fff5',  # Zalgiris
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
   team_flags = {
   'BER': '🇩🇪',  # Germany 
   'IST': '🇹🇷',  # Turkey
   'MCO': '🇲🇨',  # Monaco
   'BAS': '🇪🇸',  # Spain
   'RED': '🇷🇸',  # Serbia
   'MIL': '🇮🇹',  # Italy
   'BAR': '🇪🇸',  # Spain
   'MUN': '🇩🇪',  # Germany
   'ULK': '🇹🇷',  # Turkey
   'ASV': '🇫🇷',  # France 
   'TEL': '🇮🇱',  # Israel
   'OLY': '🇬🇷',  # Greece
   'PAN': '🇬🇷',  # Greece
   'PRS': '🇫🇷',  # France
   'PAR': '🇷🇸',  # Serbia
   'MAD': '🇪🇸',  # Spain
   'VIR': '🇮🇹',  # Italy
   'ZAL': '🇱🇹',  # Lithuania
}

   
   team_stats, player_statsTeam1, player_statsTeam2 = create_sample_data_euroleague()
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
           color: rgba(0,0,0,0.9);
           white-space: nowrap;
           overflow: hidden;
           text-overflow: ellipsis;
       }
.team-stats-euroleague-container {
    background-color: white;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(100, 100, 100, .5);
    margin-top: -25px !important;
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
    color: #1a1f36;
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

   team_stats_area, spacing1, logo_area,  stats_area = st.columns([1.4, 0.9, 4,  2.5])
   
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
            background: linear-gradient(to bottom, #ffffff, #f5f5f7);
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
   <div style="display: flex; align-items: center; gap: 1px; justify-content: center;">
       <div style="width: 40px; height: 40px; display: flex; align-items: center;">
           <img src="{away_logo}" alt="Logo" style="width: 100%; height: 650px; object-fit: contain;">
       </div>
       <span>{team_stats_df.columns[1]}</span>
   </div>
</th>
<th>
   <div style="display: flex; align-items: center; gap: 1px; justify-content: center;">
       <div style="width: 40px; height: 40px; display: flex; align-items: center;">
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
               else f'<td class="numeric" style="text-align: center"><div style="margin-left: -2px;font-size: 12px;margin-right:-5px;"><span class="highlight" style="padding: 3px 3px; border-radius: 4px; background-color: {euroleague_team_colors[team_stats_df.columns[1]] if (idx == 1 and ((value > row[2] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[2] and row.iloc[0] in ["TO%", "TO"]))) else "transparent"}">{value:.1f}{"%" if str(row.iloc[0]).endswith("%") else ""}</span>{f"<img src=\'{away_logo}\' style=\'width: 28px; height: 28px; margin-left: 2px; vertical-align: middle;\'/>" if (idx == 1 and ((value > row[2] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[2] and row.iloc[0] in ["TO%", "TO"]))) else ""}</div></td>' 
               if isinstance(value, (int, float)) and idx == 1
               else f'<td class="numeric" style="text-align: center"><div style="margin-left: -2px;font-size: 12px;margin-right:-5px;"><span class="highlight" style="padding: 3px 3px; border-radius: 4px; background-color: {euroleague_team_colors[team_stats_df.columns[2]] if (idx == 2 and ((value > row[1] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[1] and row.iloc[0] in ["TO%", "TO"]))) else "transparent"}">{value:.1f}{"%" if str(row.iloc[0]).endswith("%") else ""}</span>{f"<img src=\'{home_logo}\' style=\'width: 28px; height: 28px; margin-left: 2px; vertical-align: middle;\'/>" if (idx == 2 and ((value > row[1] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[1] and row.iloc[0] in ["TO%", "TO"]))) else ""}</div></td>' 
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
                      <span style='font-size: 16px; color: #1a1f36; font-weight: 500;'>@</span>
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
                   <div style="display: flex; align-items: center; justify-content: center; gap: 1px; padding: 0px; margin-left:0px;">
                       <div style="width: 40px; height: 40px; display: flex; align-items: center;">
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
   margin-top: -540px !important;
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
    margin-top: -520px !important;
}

.player-stats-table {
    font-size: 11px !important;


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
      
      # Create the buttons
      with btn1:
          if st.button('All', key='game_view_btn'):
              st.session_state.selected_view = 'All'
      with btn2:
          if st.button(home_team, key='home_team_btn'):
              st.session_state.selected_view = 'Home'
      with btn3:
          if st.button(away_team, key='away_team_btn'):
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
    'HAP': '#ec1c24',  # Hapoel Tel Aviv
    'JOV': '#006241',  # Joventut
    'ULM': '#f47920',  # Ulm
    'SOP': '#ffd700',  # Sopot
    'TTK': '#00b4e3',  # Turk Telekom
    'CLU': '#000000',  # Cluj
    'VNC': '#7b2132',  # Venice
    'VAL': '#f47a38',  # Valencia
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
    'HAP': '#ffd0d2',  # Light Red (darker)
    'JOV': '#ccffe0',  # Light Green (darker)
    'ULM': '#ffe0cc',  # Light Orange (darker)
    'SOP': '#ffe4b3',  # Light Yellow (darker)
    'TTK': '#ccf2ff',  # Light Blue (darker)
    'CLU': '#e6e6e6',  # Light Gray (darker)
    'VNC': '#ffd6e0',  # Light Burgundy (darker)
    'VAL': '#ffe0cc',  # Light Orange (darker)
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
    'HAP': 'HAPOEL TEL AVIV',
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
           color: rgba(0,0,0,0.9);
           white-space: nowrap;
           overflow: hidden;
           text-overflow: ellipsis;
       }
.team-stats-eurocup-container {
    background-color: white;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(100, 100, 100, .5);
    margin-top: -25px !important;
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
    color: #1a1f36;
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

   team_stats_area, spacing1, logo_area,  stats_area = st.columns([1.4, 0.9, 4,  2.5])
   
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
            background: linear-gradient(to bottom, #ffffff, #f5f5f7);
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
   <div style="display: flex; align-items: center; gap: 1px; justify-content: center;">
       <div style="width: 40px; height: 40px; display: flex; align-items: center;">
           <img src="{away_logo}" alt="Logo" style="width: 100%; height: 650px; object-fit: contain;">
       </div>
       <span>{team_stats_df.columns[1]}</span>
   </div>
</th>
<th>
   <div style="display: flex; align-items: center; gap: 1px; justify-content: center;">
       <div style="width: 40px; height: 40px; display: flex; align-items: center;">
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
               else f'<td class="numeric" style="text-align: center"><div style="margin-left: -2px;font-size: 12px;margin-right:-5px;"><span class="highlight" style="padding: 3px 3px; border-radius: 4px; background-color: {eurocup_team_colors_light[team_stats_df.columns[1]] if (idx == 1 and ((value > row[2] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[2] and row.iloc[0] in ["TO%", "TO"]))) else "transparent"}">{value:.1f}{"%" if str(row.iloc[0]).endswith("%") else ""}</span>{f"<img src=\'{away_logo}\' style=\'width: 28px; height: 28px; margin-left: 2px; vertical-align: middle;\'/>" if (idx == 1 and ((value > row[2] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[2] and row.iloc[0] in ["TO%", "TO"]))) else ""}</div></td>' 
               if isinstance(value, (int, float)) and idx == 1
               else f'<td class="numeric" style="text-align: center"><div style="margin-left: -2px;font-size: 12px;margin-right:-5px;"><span class="highlight" style="padding: 3px 3px; border-radius: 4px; background-color: {eurocup_team_colors_light[team_stats_df.columns[2]] if (idx == 2 and ((value > row[1] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[1] and row.iloc[0] in ["TO%", "TO"]))) else "transparent"}">{value:.1f}{"%" if str(row.iloc[0]).endswith("%") else ""}</span>{f"<img src=\'{home_logo}\' style=\'width: 28px; height: 28px; margin-left: 2px; vertical-align: middle;\'/>" if (idx == 2 and ((value > row[1] and row.iloc[0] not in ["TO%", "TO"]) or (value < row[1] and row.iloc[0] in ["TO%", "TO"]))) else ""}</div></td>' 
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
                      <span style='font-size: 16px; color: #1a1f36; font-weight: 500;'>@</span>
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
                   <div style="display: flex; align-items: center; justify-content: center; gap: 1px; padding: 0px; margin-left:0px;">
                       <div style="width: 40px; height: 40px; display: flex; align-items: center;">
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
   margin-top: -540px !important;
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
    margin-top: -520px !important;
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
    'HAP': ['#ff9999', '#ffb3b3', '#ffcccc', '#ffe6e6', '#fff0f0', '#fff5f5'],
    
    # Yellow/Gold shades
    'CAN': ['#ffd480', '#ffdb99', '#ffe6b3', '#fff0cc', '#fff5e6', '#fff9f0'],
    
    # Orange shades
    'ULM': ['#ffb380', '#ffc299', '#ffd1b3', '#ffe0cc', '#fff0e6', '#fff5f0'],
    'VAL': ['#ffb380', '#ffc299', '#ffd1b3', '#ffe0cc', '#fff0e6', '#fff5f0'],
    
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


















def main():
    st.set_page_config(layout="wide", page_icon="🏀", page_title="Eurolytics")
    
    st.markdown("""
    <style>
        /* Target the main app container */
        [data-testid="stAppViewContainer"] {
            max-width: 950px !important;
            min-width: 950px !important;
            background: #f0f0f0 !important;
            padding: .5rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
            margin: 0 auto !important; /* Center the container */
            margin-top: -60px !important;
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
        .stTabs [data-baseweb="tab-list"] {
            max-width: 100% !important;
            margin-top: -80px;
        }

        /* Fix select box width */
        [data-testid="stSelectbox"] {
            max-width: 350px !important;
            margin: 0 auto !important;
            margin-left:-10px;
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

    <div class="logo-text">EUROLYTICS</div>
    """, unsafe_allow_html=True)

    # Start fixed-width container
    st.markdown('<div class="fixed-width-container">', unsafe_allow_html=True)



    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pickle_path = os.path.join(script_dir, 'data', 'euroleague_simulations.pkl')
    with open(pickle_path, 'rb') as f:
        simulation_results_df = pickle.load(f)

    st.markdown("""
       <style>
.stTabs [data-baseweb="tab-list"] [data-baseweb="tab"] *,
    .stTabs [data-baseweb="tab-list"] [role="tab"] * {
        font-size: 11px !important;
        font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif !important;
        font-weight: 800 !important;

    }

    /* Tab container and sizing */
    .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"],
    .stTabs [data-baseweb="tab-list"] [role="tab"] {
        padding: 0px 48px !important;
        height: auto !important;
        text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
        min-height: 25px !important;
    }

    /* Selected tab styling */
    .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"][aria-selected="true"] {
        color: #2d63e2 !important;
        background: rgba(45, 99, 226, 0.12) !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 8px rgba(45, 99, 226, 0.15) !important;
text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    }

    /* Tab list container */



       /* Global styles */
  


       /* Tab styling */
       .stTabs [data-baseweb="tab-list"] {
           gap: 0;
           background: white;
           padding: 4px;
           box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
           position: sticky;
           border-radius: 8px;
           font-size: 12px;
       }

       .stTabs [data-baseweb="tab"] {
           padding: 12px 24px;
           color: #1a1f36;
           font-weight: 500;
           font-size: 12px;
           border-radius: 8px;
           transition: all 0.2s ease;
           background: transparent;
       }

       .stTabs [data-baseweb="tab"][aria-selected="true"] {
           color: #2d63e2;
           background: rgba(45, 99, 226, 0.1);
           font-weight: 600;
       }

       .stTabs [data-baseweb="tab"]:hover {
           background: rgba(0, 0, 0, 0.05);
       }

    .summary-stats-euroleague table,
    .summary-stats-eurocup table {

        border-collapse: collapse;
        border-radius: 16px;
        overflow: hidden;
        border: 2px solid white !important;
        margin-top: 5px;
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
    margin-top: -28px;
    margin-left: -15px;
    font-weight: 700;
    border: 2px solid #E0E7FF; /* Softer border color */
    border-radius: 10px; /* Slightly more rounded corners */
    padding: 2px 8px;
    height: 31px;
    min-height: 31px !important;
    background-color: #F5F7FF !important; /* Soft, light blue background */
    color: #3B82F6; /* More vibrant blue text */
    font-size: 12px;
    transition: all 0.2s ease-in-out;
    box-shadow: 0px 1px 4px rgba(45, 99, 226, 0.2); /* Softer shadow */
    display: flex;
    align-items: center;
}

/* Target the inner select button */
.stSelectbox > div[data-baseweb="select"] > div {
    height: 20px !important;
    min-height: 20px !important;
    display: flex;
    align-items: center;
}

/* Target the value container */
.stSelectbox [data-baseweb="select"] [data-testid="stMarkdownContainer"] {
    line-height: 1.2;
    padding-top: 0;
    padding-bottom: 0;
    display: flex;
    align-items: center;
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
       </style>
   """, unsafe_allow_html=True)



    
    sport_tabs = st.tabs(["Euroleague", "EuroCup"])
    
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
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
    
    with sport_tabs[0]:
        # Create three columns for the controls
        col0, col1, col2 = st.columns([.3, 2.8, 2.6])
        
        with col0:
            # Get the maximum round value from the entire dataset
            max_round = simulation_results_df['Round'].max()
            st.markdown(
                f"""
                <div style="background-color: white; border-radius: 8px; padding: 6px 6px; margin-left:-60px;
                    margin-top: 0px; box-shadow: 0 4px 12px rgba(100, 100, 100, .4);
                    display: flex; justify-content: center; align-items: center;">
                    <div style="text-align: center;font-weight: 700;  font-size: 12px;">{max_round}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col1:
            selected_matchup = st.selectbox(
                'Select Matchup',
                matchups,
                key='simulate_matchup_select',
                label_visibility='hidden'
            )
        
        with col2:
            matchup_data = simulation_results_df[simulation_results_df['Matchup'] == selected_matchup].iloc[0]
            time_value = matchup_data.get('Time', 'N/A')
            arena_value = matchup_data.get('Arena', 'N/A')
            
            st.markdown(
                f"""
                <div style="background-color: white; border-radius: 8px; padding: 5px 8px; 
                    margin-top: 0px; box-shadow: 0 4px 6px rgba(100, 100, 100, .4);margin-right:-50px; margin-left:-27px;
                    display: flex; justify-content: center; align-items: center; gap: 30px;">
                    <div style="text-align: center; font-weight: 700;  font-size: 12px; font-color: #1a4fca;">{time_value}</div>
                    <div style="text-align: center; font-weight: 700;  font-size: 12px; font-color: #1a4fca;">{arena_value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        render_stats_tables_euroleague(selected_matchup, matchups, "simulate")
        

    
    with sport_tabs[1]:
        with sport_tabs[1]:
            # Create three columns for the controls
            col0, col1, col2 = st.columns([.3,2.8,2.6])
            
            # Load EuroCup data
            team_stats_eurocup, player_statsTeam1_eurocup, player_statsTeam2_eurocup = create_sample_data_eurocup()
            if 'team_stats_eurocup' not in st.session_state:
                st.session_state['team_stats_eurocup'] = team_stats_eurocup
            if 'player_statsTeam1_eurocup' not in st.session_state:
                st.session_state['player_statsTeam1_eurocup'] = player_statsTeam1_eurocup
            if 'player_statsTeam2_eurocup' not in st.session_state:
                st.session_state['player_statsTeam2_eurocup'] = player_statsTeam2_eurocup

            # Get EuroCup matchups
            matchups_eurocup = team_stats_eurocup['Matchup'].unique().tolist()

            # Load EuroCup simulation results
            script_dir = os.path.dirname(os.path.abspath(__file__))
            pickle_path_eurocup = os.path.join(script_dir, 'data', 'eurocup_simulations.pkl')
            with open(pickle_path_eurocup, 'rb') as f:
                simulation_results_df_eurocup = pickle.load(f)
            
            if 'simulation_results_df_eurocup' not in st.session_state:
                st.session_state['simulation_results_df_eurocup'] = simulation_results_df_eurocup
            
            with col0:
            # Get the maximum round value from the entire dataset
                max_round = simulation_results_df['Round'].max()
                st.markdown(
                f"""
                <div style="background-color: white; border-radius: 8px; padding: 6px 6px; margin-left:-60px;
                    margin-top: 0px; box-shadow: 0 4px 12px rgba(100, 100, 100, .4);
                    display: flex; justify-content: center; align-items: center;">
                    <div style="text-align: center;font-weight: 700;  font-size: 12px;">{max_round}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
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
                <div style="background-color: white; border-radius: 8px; padding: 5px 8px; 
                    margin-top: 0px; box-shadow: 0 4px 6px rgba(100, 100, 100, .4);margin-right:-50px; margin-left:-27px;
                    display: flex; justify-content: center; align-items: center; gap: 30px;">
                    <div style="text-align: center; font-weight: 700;  font-size: 12px; font-color: #1a4fca;">{time_value}</div>
                    <div style="text-align: center; font-weight: 700;  font-size: 12px; font-color: #1a4fca;">{arena_value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            render_stats_tables_eurocup(selected_matchup_eurocup, matchups_eurocup, simulation_results_df_eurocup, "simulate")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) 

if __name__ == "__main__":
    main()