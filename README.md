# NBA Fantasy App

This repository has a Streamlit app that lets you create your NBA fantasy team and compete against computer-generated teams. The app uses a Snowflake database that contains historical NBA playeer data.

To determine the winner of each game, the app employs a functional Keras model that was trained using the 2018 season's results. The model uses season averages in stats from the starting five players as features against thier wins and losses.

The app doesn't consider changes in playstyle or the three-point line.

## Game
Play the game [here](https://nba-gemenielabs.streamlit.app/).

## Usage
To use this app, launch the Streamlit App using the following command install streamlit and then run it:

```pip install streamlit```

```streamlit run app.py```


## License

This repository is licensed under the MIT License.
