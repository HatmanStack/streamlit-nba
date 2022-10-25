import streamlit as st
import pandas as pd
import snowflake.connector


st.header('Build Your Team')

player_add = st.text_input('Who\'s your first Pick?', 'James')


search_string = 'select full_name, first_name, last_name from NBA where full_name=\'{}\' or first_name=\'{}\' or last_name=\'{}\';'.format(player_add, player_add, player_add)


def find_player():
  my_cnx = snowflake.connector.connect(**st.secrets["snowflake"])
  data = get_player()
  my_cnx.close()
  return data


def get_player():
  with cnx.cursor() as cur:
    cur.execute(search_string)
    return cur.fetchall()

player_search = find_player()

print([player[0] for player in player_search])
player = st.selectbox('Search Results', [player[0] for player in player_search])
"""

all_players = cnx.cursor.execute('SELECT full_name from NBA;')
home_team.append(player)
if players_selected < 5:
    players_selected = st.multiselect("Your Team:", list(all_players), home_team)


players_selected = if len(players_selected) < 5: st.multiselect("Your Team:", list(all_players), home_team)


difficulty = st.radio(
    "How good is the other Team",
    ('Regular','93\' Bulls', 'All-Stars', 'DreamTeam'))
stats = []
if difficulty == 'Regular':
    st.write('Nancy.')
    stats = [850, 400, 200, 60]   
elif difficulty == '93\' Bulls':
    st.write('True Fan')
    stats = [1050, 500, 300, 80]
elif difficulty == 'All-Stars':
    st.write('Getting Warmer')
    stats = [1250, 600, 400, 100]
elif difficulty == 'DreamTeam':
    st.write('Stud')
    stats = [1450, 700, 500, 120]
else:
    st.write("You didn't select a difficulty.")
query_strings=[]
query_strings.append('SELECT * FROM (select * from NBA where PTS > {}) sample (2 rows);'.format(stats[0]))
query_strings.append('SELECT * FROM (select * from NBA where REB > {}) sample (1 rows);'.format(stats[1]))
query_strings.append('SELECT * FROM (select * from NBA where AST > {}) sample (1 rows);'.format(stats[2]))
query_strings.append('SELECT * FROM (select * from NBA where STL > {}) sample (1 rows);'.format(stats[3]))
away_team = pd.DataFrame()
for i in query_strings:
    away_team.append(cnx.cursor.execute(i))
    while not away_team['full_name'].is_unique:
      away_team = away_team[:-1, :]
      away_team.append(cnx.cursor.execute(i))



print(away_team['full_name'])


#dataframe = create_df([nba_players[100], nba_players[101]])
#print(dataframe)
#st.dataframe(create_df(players_selected))

#if st.button('Add Player'):
#  possible_players = [];
#  if len(players_selected) < 5:
#    for i in nba_players:
#        if player_add.lower in i.values():
#            possible_players.append(i)
#    player = possible_players
#    if len(possible_players) > 1:
#        player = st.selectbox(possible_players)
#    players_selected.append(player['full_name'])


st.header('Opossing Team')

#players_selected_away = st.multiselect("Away Team:", list([]), players_away['full_name'].to_list)
#st.dataframe(create_df(players_away))
"""




