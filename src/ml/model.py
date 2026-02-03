"""Machine learning model loading and prediction with caching."""

import logging
from pathlib import Path

import numpy as np
import streamlit as st
from tensorflow.keras.models import Model, load_model

logger = logging.getLogger("streamlit_nba")

# Default model path
DEFAULT_MODEL_PATH = Path("winner.keras")


class ModelLoadError(Exception):
    """Raised when model loading fails."""

    pass


@st.cache_resource
def get_winner_model(model_path: str | Path = DEFAULT_MODEL_PATH) -> Model:
    """Load and cache the winner prediction model.

    Uses Streamlit's cache_resource to ensure model is only loaded once
    per session, improving performance significantly.

    Args:
        model_path: Path to the Keras model file

    Returns:
        Loaded Keras model

    Raises:
        ModelLoadError: If model cannot be loaded
    """
    path = Path(model_path)
    if not path.exists():
        logger.error(f"Model file not found: {path}")
        raise ModelLoadError(f"Model file not found: {path}")

    try:
        logger.info(f"Loading model from {path}")
        model = load_model(str(path))
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise ModelLoadError(f"Failed to load model: {e}") from e


def predict_winner(combined_stats: np.ndarray) -> tuple[float, int]:
    """Predict game winner from combined team stats.

    Args:
        combined_stats: Numpy array of shape (1, 100) containing
            home team stats followed by away team stats

    Returns:
        Tuple of (probability, prediction) where:
            - probability: Float between 0-1 (sigmoid output)
            - prediction: 0 (away wins) or 1 (home wins)

    Raises:
        ModelLoadError: If model cannot be loaded
        ValueError: If input shape is invalid
    """
    if combined_stats.shape != (1, 100):
        raise ValueError(
            f"Expected input shape (1, 100), got {combined_stats.shape}"
        )

    model = get_winner_model()
    sigmoid_output = model.predict(combined_stats, verbose=0)
    probability = float(sigmoid_output[0][0])
    prediction = int(np.round(probability))

    logger.info(f"Prediction: probability={probability:.4f}, winner={prediction}")
    return probability, prediction


def analyze_team_stats(
    home_stats: list[list[float]], away_stats: list[list[float]]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Prepare team stats for model prediction.

    Flattens per-player stats into team-level arrays suitable for
    the prediction model.

    Args:
        home_stats: List of stat lists for each home player
        away_stats: List of stat lists for each away player

    Returns:
        Tuple of (home_array, away_array, combined_array) where:
            - home_array: Shape (1, 50) - home team flattened stats
            - away_array: Shape (1, 50) - away team flattened stats
            - combined_array: Shape (1, 100) - both teams for prediction
    """
    home_flat: list[float] = []
    away_flat: list[float] = []

    for player_stats in home_stats:
        home_flat.extend(player_stats)

    for player_stats in away_stats:
        away_flat.extend(player_stats)

    home_array = np.array(home_flat).reshape(1, -1)
    away_array = np.array(away_flat).reshape(1, -1)
    combined_array = np.array(home_flat + away_flat).reshape(1, -1)

    return home_array, away_array, combined_array
