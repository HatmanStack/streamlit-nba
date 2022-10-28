import streamlit as st
import pandas as pd
import snowflake.connector
import os

def on_page_load():
    st.set_page_config(layout="wide")
on_page_load()

stats = st.session_state.away_stats
team_match=True

if not st.session_state.home_team_df.shape[0] == 5:
  st.markdown("<h1 style='text-align: center; color: red;'>Your Team Doesn't Have 5</h1>", unsafe_allow_html=True)
  team_match = False   

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

away_data = find_away_team()
st.markdown("<h1 style='text-align: center; color: steelblue;'>Home Team</h1>", unsafe_allow_html=True)
st.dataframe(st.session_state.home_team_df)
st.markdown("<h1 style='text-align: center; color: steelblue;'>Opposing Team</h1>", unsafe_allow_html=True)
st.dataframe(away_data)

if st.button("Play New Team"):
    print("New Team")

