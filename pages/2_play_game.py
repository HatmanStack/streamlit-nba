import streamlit as st
import pandas as pd
import snowflake.connector
import numpy as np
from tensorflow.keras.models import load_model

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
else:
    away_data = find_away_team()
    
def analyze_stats(home_stats, away_stats):
    arr = []
    for j in range(len(home_stats)):
        arr += home_stats[j]
    for j in range(len(away_stats)):
        arr += away_stats[j]
    return np.array(arr).reshape(1, -1)

if teams_good:
    #first pass algo to determine winner
    cols = ['PTS', 'OREB', 'DREB', 'AST', 'STL', 'BLK', 'TOV', 'FG3_PCT', 'FT_PCT', 'FGM']
    home_stats = st.session_state.home_team_df[cols].values.tolist()
    away_stats = away_data[cols].values.tolist()
    X = analyze_stats(home_stats, away_stats)
    model = load_model('my_model')
    prediction = model.predict(X)
    winner = 'You Won' if prediction > 80 else 'Computer Won'

st.markdown("<h1 style='text-align: center; color: steelblue;'>Home Team</h1>", unsafe_allow_html=True)
st.dataframe(st.session_state.home_team_df)
if teams_good:
    st.markdown(f"<h1 style='text-align: center; color: steelblue;'>{winner}</h1>", unsafe_allow_html=True)
    
st.markdown("<h1 style='text-align: center; color: steelblue;'>Opposing Team</h1>", unsafe_allow_html=True)
st.dataframe(away_data)

if st.button("Play New Team"):
    print("New Team")

