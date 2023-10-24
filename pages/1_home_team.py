import streamlit as st
import pandas as pd
import snowflake.connector
import os

def on_page_load():
    st.set_page_config(layout="wide")
on_page_load()

col1, col2, col3 = st.columns(3)

with col2:
    st.markdown("<h1 style='text-align: center; color: steelblue;'>Build Your Team</h1>", unsafe_allow_html=True)
    player_add = st.text_input('Who\'re you picking?', 'James')
    player = player_add.lower()
st.markdown("<p style='text-align: center; color: steelblue;'>Search for a player to populate the dropdown menu then pick and save your team before searching for another player.</p>", unsafe_allow_html=True)
search_string = 'select full_name from NBA where full_name_lower=\'{}\' or first_name_lower=\'{}\' or last_name_lower=\'{}\';'.format(player, player, player)

if 'home_team' not in st.session_state:
        st.session_state['home_team'] = []
if 'away_team' not in st.session_state:
        st.session_state['away_team'] = []
if 'away_stats' not in st.session_state:
    st.session_state['away_stats'] = []
if 'home_team_df' not in st.session_state:
    st.session_state['home_team_df'] = pd.DataFrame()
if 'radio_index' not in st.session_state:
    st.session_state['radio_index'] = 0

def find_player():
  cnx = snowflake.connector.connect(**st.secrets["snowflake"])
  data = get_player(cnx)
  cnx.close()
  return data

def get_player(cnx):
  with cnx.cursor() as cur:
    cur.execute(search_string)
    return cur.fetchall()

player_search = find_player()

def find_home_team():
    test =[]
    cnx = snowflake.connector.connect(**st.secrets["snowflake"])
    print('find home team')
    for i in st.session_state.home_team:
        with cnx.cursor() as cur:
            cur.execute('SELECT * FROM NBA WHERE FULL_NAME=\'{}\''.format(i))
            test.append(cur.fetchall()[0])
    cnx.close()    
    df = pd.DataFrame(test, columns=['FULL_NAME', 'AST', 'BLK', 'DREB', 'FG3A', 'FG3M', 'FG3_PCT', 'FGA', 'FGM', 'FG_PCT', 'FTA', 'FTM', 'FT_PCT','GP', 'GS', 'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TOV', 'FIRST_NAME', 'LAST_NAME', 'FULL_NAME_LOWER', 'FIRST_NAME_LOWER', 'LAST_NAME_LOWER', 'IS_ACTIVE'])
    st.session_state.home_team_df = df
    return df

home_team_df = find_home_team()

player_search = [player[0] for player in player_search]
if not home_team_df.empty:
    name_list = home_team_df['FULL_NAME'].tolist()
    player_search += name_list

def save_state():
    saved_players = home_team_df['FULL_NAME'].tolist()
    holder = saved_players + player_selected
    if len(player_selected) > len(saved_players):
        for i in holder:
            if i not in st.session_state.home_team:
                st.session_state.home_team.append(i)
    elif len(player_selected) < len(saved_players):
        for i in saved_players:
            if i not in player_selected:
                st.session_state.home_team.remove(i)
    st.rerun()

col1, col2 = st.columns([7,1])
with col1:
    player_selected = st.multiselect("Search Results:", player_search, home_team_df['FULL_NAME'].tolist(), label_visibility="collapsed")
with col2:
    if st.button('Save Team'):
        save_state()

st.markdown("<h1 style='text-align: center; color: steelblue;'>Preview</h1>", unsafe_allow_html=True)
   
st.dataframe(home_team_df)
radio_index = st.session_state.radio_index
col1, col2, col3, col4, col5 = st.columns(5)
with col3:
    st.markdown("<h3 style='text-align: center; color: steelblue;'>Away Team</h3>", unsafe_allow_html=True)
    difficulty = st.radio(
        label="Difficulty", index=radio_index, options=['Regular','93\' Bulls', 'All-Stars', 'Dream Team'],
        label_visibility="collapsed", )

    if difficulty == 'Regular':
        st.session_state.away_stats = [850, 400, 200, 60]
        st.session_state.radio_index = 0       
    elif difficulty == '93\' Bulls':
        st.session_state.away_stats = [1050, 500, 300, 80]
        st.session_state.radio_index = 1
    elif difficulty == 'All-Stars':
        st.session_state.away_stats = [1250, 600, 400, 100]
        st.session_state.radio_index = 2
    elif difficulty == 'Dream Team':
        st.session_state.away_stats = [1450, 700, 500, 120]
        st.session_state.radio_index = 3
    else:
        st.write("You didn't select a difficulty.")

    
  



