import streamlit as st
import pandas as pd
import snowflake.connector
import numpy as np
from tensorflow.keras.models import load_model
import random
import math

def on_page_load():
    st.set_page_config(layout="wide")
on_page_load()

stats = st.session_state.away_stats    
teams_good = True

query_string = ('SELECT * FROM (select * from NBA where PTS > {}) sample (2 rows) UNION '.format(stats[0]))
query_string += ('SELECT * FROM (select * from NBA where REB > {}) sample (1 rows) UNION '.format(stats[1]))
query_string += ('SELECT * FROM (select * from NBA where AST > {}) sample (1 rows) UNION '.format(stats[2]))
query_string += ('SELECT * FROM (select * from NBA where STL > {}) sample (1 rows);'.format(stats[3]))

def get_away_team(cnx, query_string):
    with cnx.cursor() as cur:
        cur.execute(query_string)
        players = cur.fetchall()
        while len(players) != 5:
            cur.execute(query_string)   
            players = cur.fetchall()
    return players    
              
def find_away_team():
    cnx = snowflake.connector.connect(**st.secrets["snowflake"])
    data = get_away_team(cnx, query_string)
    cnx.close()
    df = pd.DataFrame(data, columns=['FULL_NAME', 'AST', 'BLK', 'DREB', 'FG3A', 'FG3M', 'FG3_PCT', 'FGA', 'FGM', 'FG_PCT', 'FTA', 'FTM', 'FT_PCT','GP', 'GS', 'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TOV', 'FIRST_NAME', 'LAST_NAME', 'IS_ACTIVE'])
    return df   

if not st.session_state.home_team_df.shape[0] == 5:
    st.markdown("<h3 style='text-align: center; color: red;'>Your Team Doesn't Have 5</h3>", unsafe_allow_html=True)
    away_data = pd.DataFrame()
    teams_good = False
    winner = ''
else:
    away_data = find_away_team()
    
def analyze_stats(home_stats, away_stats):
    home=[]
    away=[]
    for j in range(len(home_stats)):
        home += home_stats[j]
    for j in range(len(away_stats)):
        away += away_stats[j]
    return np.array(home).reshape(1,-1), np.array(away).reshape(1,-1), np.array(home + away).reshape(1, -1)

def get_score_board(p_pred, w_score):
    score = []
    quarter_score = w_score/4
    score.append(int(quarter_score + random.randint(-10, 10), 100))
    score.append(int(quarter_score + random.randint(-10, 10)))
    score.append(int(quarter_score + random.randint(-10, 10)))
    score.append(w_score - (score[0] + score[1] + score[2]))
    score.append(w_score)
    return score

if teams_good:
    #first pass algo to determine winner
    cols = ['PTS', 'OREB', 'DREB', 'AST', 'STL', 'BLK', 'TOV', 'FG3_PCT', 'FT_PCT', 'FGM']
    home_stats = st.session_state.home_team_df[cols].values.tolist()
    away_stats = away_data[cols].values.tolist()
    home, away, winner = analyze_stats(home_stats, away_stats)
    
    winner_model = load_model('winner_model')
    home_team_model = load_model('home_team_model')
    away_team_model = load_model('away_team_model')

    winner_prediction = winner_model.predict(winner)
    home_point_prediction = home_team_model.predict(home)
    away_point_prediction = away_team_model.predict(away)
    
    score = []
    winner_score = random.randint(90, 130)
    loser_score = random.randint(80, 120)
    while winner_score < loser_score:
        winner_score = random.randint(90, 130)
        loser_score = random.randint(80, 120)

    if winner_prediction > 100:
        score.append(get_score_board(winner_prediction, winner_score))
        score.append(get_score_board(away_point_prediction, loser_score))
        winner = 'Winner'
    else:
        score.append(get_score_board(winner_prediction, loser_score))
        score.append(get_score_board(away_point_prediction, winner_score))
        winner = 'Loser'

    box_score = pd.DataFrame(score , columns=['1', '2', '3', '4', 'Final'], index=['Home Team', 'Away Team'] )
    
    print(f"Prediction: {winner_prediction}")
    print(f"Home Points: {home_point_prediction}")
    print(f"Away Points: {away_point_prediction}")

st.markdown("<h1 style='text-align: center; color: steelblue;'>Home Team</h1>", unsafe_allow_html=True)
st.dataframe(st.session_state.home_team_df)
if teams_good:
    print(f"Teams Good")
    st.markdown(f"<h3 style='text-align: center; color: steelblue;'>{winner}</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col2:
      st.dataframe(box_score)
st.markdown("<h1 style='text-align: center; color: steelblue;'>Away Team</h1>", unsafe_allow_html=True)
st.dataframe(away_data)

if st.button("Play New Team"):
    print("New Team")

