"""Session state management for the Streamlit application."""

import logging
from typing import cast

import pandas as pd
import streamlit as st

from src.config import DIFFICULTY_PRESETS

logger = logging.getLogger("streamlit_nba")

# Default difficulty preset
DEFAULT_DIFFICULTY = "Regular"


def init_session_state() -> None:
    """Initialize all session state keys with safe defaults.

    This should be called at the start of each page to ensure
    all required state keys exist before access.
    """
    defaults = {
        "home_team": [],
        "away_team": [],
        "away_team_df": pd.DataFrame(),
        "away_stats": list(DIFFICULTY_PRESETS[DEFAULT_DIFFICULTY]),
        "home_team_df": pd.DataFrame(),
        "radio_index": 0,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
            logger.debug("Initialized session state: %s", key)


def get_away_stats() -> list[int]:
    """Safely get away team stats from session state.

    Returns:
        List of stat thresholds [pts, reb, ast, stl], or defaults if not set
    """
    init_session_state()  # Ensure state is initialized
    stats = st.session_state.get("away_stats")

    if stats is None or not isinstance(stats, list) or len(stats) != 4:
        logger.warning("Invalid away_stats in session, using defaults")
        default_stats = list(DIFFICULTY_PRESETS[DEFAULT_DIFFICULTY])
        st.session_state["away_stats"] = default_stats
        return default_stats

    return cast("list[int]", stats)


def get_home_team_df() -> pd.DataFrame:
    """Safely get home team DataFrame from session state.

    Returns:
        DataFrame with home team player data, or empty DataFrame if not set
    """
    init_session_state()
    df = st.session_state.get("home_team_df")

    if df is None or not isinstance(df, pd.DataFrame):
        logger.warning("Invalid home_team_df in session, using empty DataFrame")
        return pd.DataFrame()

    return cast("pd.DataFrame", df)
