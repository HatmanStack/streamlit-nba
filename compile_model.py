import pandas as pd
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.losses import BinaryCrossentropy
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from scikeras.wrappers import KerasClassifier 

def create_stats(roster, schedule):
    home_stats = []
    away_stats = []
    S = []

    # Loading Relavent Columns from f-test
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

        # Create numpy array with all the players on the Home Team's Stats followed by the Away Team's stats    
        S.append(np.nan_to_num(np.array(arr), copy=False))
    return S

roster = pd.read_csv('player_stats.txt', delimiter=',')
schedule = pd.read_csv('schedule.txt', delimiter=',')

# Create winning condition to train on
schedule['winner'] = schedule.apply(lambda x: 0 if x['PTS'] > x['PTS.1'] else 1, axis=1) 

X = np.array(create_stats(roster, schedule))
y = np.array(schedule['winner'])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

def create_model(optimizer='rmsprop', init='glorot_uniform'):
    inputs = keras.Input(shape=(100,))
    dense = layers.Dense(50, activation="relu")
    x = dense(inputs)
    x = layers.Dense(64, activation="relu")(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    model = keras.Model(inputs=inputs, outputs=outputs, name="nba_model")
    model.compile(loss=BinaryCrossentropy(from_logits=False), optimizer=optimizer, metrics=["accuracy"])
    
    return model

model = KerasClassifier(model=create_model, verbose=0, init='glorot_uniform')

optimizer = ['SGD', 'RMSprop', 'Adagrad', 'Adadelta', 'Adam', 'Adamax', 'Nadam']
init = ['uniform', 'lecun_uniform', 'normal', 'zero', 'glorot_normal', 'glorot_uniform', 'he_normal', 'he_uniform']
epochs = [500, 1000, 1500]
batches = [50, 100, 200]
param_grid = dict(optimizer=optimizer, epochs=epochs, batch_size=batches, init=init)

random_search = RandomizedSearchCV(estimator=model, param_distributions=param_grid, n_iter=100, verbose=3)
random_search_result = random_search.fit(X_train, y_train)
best_model = random_search_result.best_estimator_

best_model.model_.save('winner.keras')
best_parameters = random_search_result.best_params_
print("Best parameters: ", best_parameters)

test_accuracy = random_search_result.best_estimator_.score(X_test, y_test)
print("Test accuracy: ", test_accuracy)
