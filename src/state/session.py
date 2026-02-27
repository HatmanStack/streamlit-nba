"""Session state management for the Streamlit application."""

import logging
from dataclasses import dataclass, field
from typing import cast

import pandas as pd
import streamlit as st

from src.config import DIFFICULTY_PRESETS

logger = logging.getLogger("streamlit_nba")

# Default difficulty preset
DEFAULT_DIFFICULTY = "Regular"


@dataclass
class GameState:
    """Dataclass representing the game session state."""

    home_team: list[str] = field(default_factory=list)
    away_team: list[str] = field(default_factory=list)
    away_stats: list[int] = field(
        default_factory=lambda: list(DIFFICULTY_PRESETS[DEFAULT_DIFFICULTY])
    )
    home_team_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    radio_index: int = 0


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
            logger.debug(f"Initialized session state: {key}")


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


def get_home_team_names() -> list[str]:
    """Safely get home team player names from session state.

    Returns:
        List of player names on home team
    """
    init_session_state()
    team = st.session_state.get("home_team")

    if team is None or not isinstance(team, list):
        return []

    return cast("list[str]", team)


def set_difficulty(preset_name: str) -> None:
    """Set the difficulty level by preset name.

    Args:
        preset_name: Name of difficulty preset
    """
    if preset_name not in DIFFICULTY_PRESETS:
        logger.error(f"Invalid difficulty preset: {preset_name}")
        return

    index = list(DIFFICULTY_PRESETS.keys()).index(preset_name)
    st.session_state["away_stats"] = list(DIFFICULTY_PRESETS[preset_name])
    st.session_state["radio_index"] = index
    logger.info(f"Set difficulty to {preset_name}")


def add_player_to_team(player_name: str) -> bool:
    """Add a player to the home team.

    Args:
        player_name: Full name of player to add

    Returns:
        True if added, False if already on team or team is full
    """
    init_session_state()
    team = st.session_state.get("home_team", [])

    if len(team) >= 5:
        logger.warning("Cannot add player: team is full")
        return False

    if player_name in team:
        logger.debug(f"Player {player_name} already on team")
        return False

    team.append(player_name)
    st.session_state["home_team"] = team
    logger.info(f"Added {player_name} to team")
    return True


def remove_player_from_team(player_name: str) -> bool:
    """Remove a player from the home team.

    Args:
        player_name: Full name of player to remove

    Returns:
        True if removed, False if not on team
    """
    init_session_state()
    team = st.session_state.get("home_team", [])

    if player_name not in team:
        logger.debug(f"Player {player_name} not on team")
        return False

    team.remove(player_name)
    st.session_state["home_team"] = team
    logger.info(f"Removed {player_name} from team")
    return True
