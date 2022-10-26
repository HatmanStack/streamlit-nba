import streamlit as st
import pandas as pd
import snowflake.connector

st.header('Build Your Team')

player_add = st.text_input('Who\'re you picking?', 'James')

search_string = 'select full_name, first_name, last_name from NBA where full_name=\'{}\' or first_name=\'{}\' or last_name=\'{}\';'.format(player_add, player_add, player_add)

if 'home_team' not in st.session_state:
        st.session_state['home_team'] = []
if 'away_team' not in st.session_state:
        st.session_state['away_team'] = []

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

player_selected = st.multiselect("Search Results:", [player[0] for player in player_search])

def player_to_add():
    cnx = snowflake.connector.connect(**st.secrets["snowflake"])
    test = []
    for i in player_selected:
        with cnx.cursor() as cur:
            string = i.replace("'", "\'")
            cur.execute('SELECT * FROM NBA WHERE FULL_NAME=\'{}\''.format(string))
            test.append(cur.fetchall()[0])
    cnx.close()    
    df = pd.DataFrame(test, columns=['FULL_NAME', 'AST', 'BLK', 'DREB', 'FG3A', 'FG3M', 'FG3_PCT', 'FGA', 'FGM', 'FG_PCT', 'FTA', 'FTM', 'FT_PCT','GP', 'GS', 'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TOV', 'FIRST_NAME', 'LAST_NAME', 'IS_ACTIVE'])
    return df

st.header('Preview')
st.dataframe(player_to_add())

def save_state():
    print('save state')
    holder = home_team_df['FULL_NAME'].tolist() + player_selected
    st.session_state.home_team = holder
    st.experimental_rerun()

def find_home_team():
    test =[]
    cnx = snowflake.connector.connect(**st.secrets["snowflake"])
    print('find home team')
    for i in st.session_state.home_team:
        with cnx.cursor() as cur:
            cur.execute('SELECT * FROM NBA WHERE FULL_NAME=\'{}\''.format(i))
            test.append(cur.fetchall()[0])
    cnx.close()    
    df = pd.DataFrame(test, columns=['FULL_NAME', 'AST', 'BLK', 'DREB', 'FG3A', 'FG3M', 'FG3_PCT', 'FGA', 'FGM', 'FG_PCT', 'FTA', 'FTM', 'FT_PCT','GP', 'GS', 'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TOV', 'FIRST_NAME', 'LAST_NAME', 'IS_ACTIVE'])
    return df

home_team_df = find_home_team()

if st.button('Add to Team'):
    save_state()

st.header('Home Team')
st.dataframe(home_team_df)

if st.button('Play Game'):
  if len(st.session_state.home_team) == 5:
    st.write('play ball') 
  else:
    st.write('It takes 5 to Tango   {}'.format(len(st.session_state.home_team)))

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

def get_away_team(cnx, query_strings):
    away_team = []
    for i in query_strings:
        with cnx.cursor() as cur:
            cur.execute(i)
            player = cur.fetchall()
            if len(player) < 2 :
                checklist = [player[0] for player in away_team]
                for i in checklist:
                    if i == player[0][0]:
                      player = cur.execute(i).fetchall()
            if len(player) > 1:
              away_team.append(player[0])
              away_team.append(player[1])
            else:
              away_team.append(player[0])
    print('Away_Team: {}'.format(away_team))
    return away_team     
              
def find_away_team():
    cnx = snowflake.connector.connect(**st.secrets["snowflake"])
    data = get_away_team(cnx, query_strings)
    cnx.close()
    return data

away_data = find_away_team()

def save_away_team():
    st.session_state.away_team = away_data

if st.button('Set Away Team'):
    save_away_team()

def create_away_df():
    if len(st.session_state.away_team)<1:
        data = away_data
    else:
        data = st.session_state.away_team
    df = pd.DataFrame(data, columns=['FULL_NAME', 'AST', 'BLK', 'DREB', 'FG3A', 'FG3M', 'FG3_PCT', 'FGA', 'FGM', 'FG_PCT', 'FTA', 'FTM', 'FT_PCT','GP', 'GS', 'MIN', 'OREB', 'PF', 'PTS', 'REB', 'STL', 'TOV', 'FIRST_NAME', 'LAST_NAME', 'IS_ACTIVE'])
    return df

st.header('Opossing Team')
st.dataframe(create_away_df())





