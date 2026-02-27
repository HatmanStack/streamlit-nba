# NBA Fantasy App

This repository has a Streamlit app that lets you create an NBA fantasy team and compete against computer-generated teams. The app uses a local CSV file that contains historical NBA player data.

To determine the winner of each game, the app uses a functional Keras model that was trained using the 2018 season's game by game results. The model uses season averages in stats from the starting five players as features against thier wins and losses. The training data and model script are included. 

The app doesn't consider changes in playstyle or the three-point line when choosing from historical players.

## Game
Play the game [here](https://hatmanstack-streamlit-nba-app-dz3nxx.streamlit.app/).

## Usage
To use this app, launch the Streamlit App using the following command install streamlit and then run it:

```
pip install -r requirements.txt
streamlit run app.py
```

## License

This repository is licensed under the MIT License.
