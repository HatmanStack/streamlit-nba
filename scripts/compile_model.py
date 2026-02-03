#!/usr/bin/env python3
"""NBA game winner prediction model training script.

This script trains a neural network to predict game winners based on
team statistics. It uses RandomizedSearchCV to find optimal hyperparameters.

Usage:
    python scripts/compile_model.py
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scikeras.wrappers import KerasClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.losses import BinaryCrossentropy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Data file paths
ROSTER_FILE = Path("player_stats.txt")
SCHEDULE_FILE = Path("schedule.txt")
OUTPUT_MODEL = Path("winner.keras")

# Feature columns from roster data
FEATURE_COLS: list[str] = [
    "TEAM",
    "PTS/G",
    "ORB",
    "DRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "3P%",
    "FT%",
    "2P",
]

# Hyperparameter search space
OPTIMIZERS: list[str] = [
    "SGD",
    "RMSprop",
    "Adagrad",
    "Adadelta",
    "Adam",
    "Adamax",
    "Nadam",
]
INITIALIZERS: list[str] = [
    "uniform",
    "lecun_uniform",
    "normal",
    "zero",
    "glorot_normal",
    "glorot_uniform",
    "he_normal",
    "he_uniform",
]
EPOCHS: list[int] = [500, 1000, 1500]
BATCH_SIZES: list[int] = [50, 100, 200]


def create_stats(
    roster: pd.DataFrame, schedule: pd.DataFrame
) -> list[np.ndarray]:
    """Create feature arrays from roster and schedule data.

    Args:
        roster: DataFrame with player statistics
        schedule: DataFrame with game schedule and scores

    Returns:
        List of numpy arrays, one per game with combined team stats
    """
    home_stats: list[list] = []
    away_stats: list[list] = []
    features: list[np.ndarray] = []

    new_roster = roster[FEATURE_COLS]

    # Get stats for each team in each game
    for team in schedule["Home/Neutral"]:
        home_stats.append(new_roster[new_roster["TEAM"] == team].values.tolist())

    for team in schedule["Visitor/Neutral"]:
        away_stats.append(new_roster[new_roster["TEAM"] == team].values.tolist())

    # Combine home and away stats for each game
    for i in range(len(home_stats)):
        arr: list[float] = []

        for j in range(len(home_stats[i])):
            del home_stats[i][j][0]  # Remove team name
            arr.extend(home_stats[i][j])

        for j in range(len(away_stats[i])):
            del away_stats[i][j][0]  # Remove team name
            arr.extend(away_stats[i][j])

        # Handle NaN values
        features.append(np.nan_to_num(np.array(arr), copy=False))

    return features


def create_model(
    optimizer: str = "rmsprop", init: str = "glorot_uniform"
) -> keras.Model:
    """Create the neural network model architecture.

    Args:
        optimizer: Optimizer name
        init: Weight initializer name

    Returns:
        Compiled Keras model
    """
    inputs = keras.Input(shape=(100,))
    x = layers.Dense(50, activation="relu", kernel_initializer=init)(inputs)
    x = layers.Dense(64, activation="relu", kernel_initializer=init)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="nba_model")
    model.compile(
        loss=BinaryCrossentropy(from_logits=False),
        optimizer=optimizer,
        metrics=["accuracy"],
    )

    return model


def train_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    n_iterations: int = 100,
) -> tuple[keras.Model, dict, float]:
    """Train model with hyperparameter search.

    Args:
        x_train: Training features
        y_train: Training labels
        x_test: Test features
        y_test: Test labels
        n_iterations: Number of random search iterations

    Returns:
        Tuple of (best_model, best_params, test_accuracy)
    """
    model = KerasClassifier(
        model=create_model,
        verbose=0,
        init="glorot_uniform",
    )

    param_grid = {
        "optimizer": OPTIMIZERS,
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZES,
        "init": INITIALIZERS,
    }

    logger.info(f"Starting randomized search with {n_iterations} iterations")

    random_search = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_grid,
        n_iter=n_iterations,
        verbose=3,
    )

    random_search_result = random_search.fit(x_train, y_train)

    best_model = random_search_result.best_estimator_
    best_params = random_search_result.best_params_
    test_accuracy = best_model.score(x_test, y_test)

    return best_model.model_, best_params, test_accuracy


def main() -> None:
    """Main training pipeline."""
    logger.info("Loading data files")

    if not ROSTER_FILE.exists():
        logger.error(f"Roster file not found: {ROSTER_FILE}")
        raise FileNotFoundError(f"Missing {ROSTER_FILE}")

    if not SCHEDULE_FILE.exists():
        logger.error(f"Schedule file not found: {SCHEDULE_FILE}")
        raise FileNotFoundError(f"Missing {SCHEDULE_FILE}")

    roster = pd.read_csv(ROSTER_FILE, delimiter=",")
    schedule = pd.read_csv(SCHEDULE_FILE, delimiter=",")

    logger.info(f"Loaded {len(roster)} players and {len(schedule)} games")

    # Create target variable: 0 = home wins, 1 = away wins
    schedule["winner"] = schedule.apply(
        lambda x: 0 if x["PTS"] > x["PTS.1"] else 1, axis=1
    )

    # Create feature arrays
    logger.info("Creating feature arrays")
    X = np.array(create_stats(roster, schedule))
    y = np.array(schedule["winner"])

    logger.info(f"Feature shape: {X.shape}, Target shape: {y.shape}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # Train model
    best_model, best_params, test_accuracy = train_model(
        X_train, y_train, X_test, y_test
    )

    # Save model
    logger.info(f"Saving model to {OUTPUT_MODEL}")
    best_model.save(OUTPUT_MODEL)

    logger.info(f"Best parameters: {best_params}")
    logger.info(f"Test accuracy: {test_accuracy:.4f}")


if __name__ == "__main__":
    main()
