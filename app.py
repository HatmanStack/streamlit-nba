import streamlit as st
import pandas as pd
import requests
import numpy as np

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players


nba_players = players.get_players()
player_names = {i['full_name'] for i in nba_players}

st.header('Build Your Team')

player_add = st.text_input('Who\'s your first Pick?', '')

playerA = 'Lebron James'
playerB = 'Kevin Durant'
players_selected = st.multiselect("Your Team:", list(player_names))

def create_df(players):
    df = pd.DataFrame()
    for i in players:
        for i in nba_players:
            if i['full_name'] == i:
                df.add(playercareerstats.PlayerCareerStats(player_id=i['id']).get_data_frames()[0])
    return df


st.dataframe(create_df(players_selected))

if st.button('Add Player'):
  possible_players = [];
  if len(players_selected) < 5:
    for i in nba_players:
        if player_add.lower in i.values():
            possible_players.append(i)
    player = possible_players
    if len(possible_players) > 1:
        player = st.selectbox(possible_players)
    players_selected.append(player['full_name'])


st.header('Opossing Team')

players_away = np.random.choice(nba_players, 5)

def get_random_away():
    players_away.append(np.random.choice(nba_players,1))

def get_player_names():
    names = []
    for i in players_away:
        names.append(i['full_name'])
    return names
names = get_player_names()
if len(players_away) < 5:
    get_random_away()
    get_player_names()


players_selected_away = st.multiselect("Your Team:", list(), names)
st.dataframe(create_df(players_away))





