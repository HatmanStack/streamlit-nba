import pandas as pd
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.losses import BinaryCrossentropy
from sklearn.model_selection import train_test_split

def create_stats(roster, schedule):
    home_stats = []
    away_stats = []
    S = []
    cols = ['TEAM','PTS/G', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', '3P%', 'FT%','2P'] 
    new_roster = roster[cols]
    for i in schedule['Home/Neutral']:
        home_stats.append((new_roster[new_roster['TEAM'] == i]).values.tolist())
    for i in schedule['Visitor/Neutral']:
        away_stats.append((new_roster.loc[new_roster['TEAM'] == i]).values.tolist())
    for i in range(len(home_stats)):
        arr = []
        for j in range(len(home_stats[i])):
            del home_stats[i][j][0]
            arr += home_stats[i][j]
        for j in range(len(away_stats[i])):
            del away_stats[i][j][0]
            arr += away_stats[i][j]    
        S.append(np.nan_to_num(np.array(arr), copy=False))
    return S

roster = pd.read_csv('roster.txt', delimiter=',')
schedule = pd.read_csv('nba.txt', delimiter=',')
schedule['winner'] = schedule.apply(lambda x: 0 if x['PTS'] > x['PTS.1'] else 1, axis=1) 

X = np.array(create_stats(roster, schedule))
y = np.array(schedule['winner'])

inputs = keras.Input(shape=(100,))
dense = layers.Dense(50, activation="relu")
x = dense(inputs)
x = layers.Dense(64, activation="relu")(x)
outputs = layers.Dense(1)(x)
model = keras.Model(inputs=inputs, outputs=outputs, name="nba_model")
model.summary()

model.compile(
    loss=BinaryCrossentropy(from_logits=True),
    optimizer=keras.optimizers.RMSprop(),
    metrics=["accuracy"],
)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
history = model.fit(X_train, y_train, batch_size=64, epochs=200, validation_split=0.2)
model.save('my_model')
test_scores = model.evaluate(X_test, y_test, verbose=2)
print("Test loss:", test_scores[0])
print("Test accuracy:", test_scores[1])
