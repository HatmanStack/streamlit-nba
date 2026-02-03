"""Home team builder page."""

import logging

import pandas as pd
import streamlit as st

from src.config import DIFFICULTY_PRESETS, PLAYER_COLUMNS
from src.database.connection import DatabaseConnectionError, QueryExecutionError, get_connection
from src.database.queries import get_players_by_full_names, search_player_by_name
from src.state.session import init_session_state
from src.utils.html import safe_heading, safe_paragraph
from src.validation.inputs import validate_search_term

logger = logging.getLogger("streamlit_nba")


def on_page_load() -> None:
    """Configure page settings."""
    st.set_page_config(layout="wide")


on_page_load()

# Initialize session state before any access
init_session_state()

col1, col2, col3 = st.columns(3)

with col2:
    safe_heading("Build Your Team", level=1, color="steelblue")
    player_add = st.text_input("Who're you picking?", "James")

safe_paragraph(
    "Search for a player to populate the dropdown menu then pick and "
    "save your team before searching for another player.",
    color="steelblue",
)


def find_player(search_term: str) -> list[str]:
    """Search for players by name with validation and error handling.

    Args:
        search_term: User-provided search term

    Returns:
        List of matching player full names
    """
    # Validate input
    validated_term = validate_search_term(search_term)
    if validated_term is None:
        st.warning("Invalid search term. Please use only letters, numbers, and basic punctuation.")
        return []

    try:
        with get_connection() as conn:
            results = search_player_by_name(conn, validated_term)
            return [player[0] for player in results]
    except DatabaseConnectionError as e:
        st.error(f"Could not connect to database. Please try again later.")
        logger.error(f"Database connection error: {e}")
        return []
    except QueryExecutionError as e:
        st.error("Error searching for players. Please try again.")
        logger.error(f"Query error: {e}")
        return []


def find_home_team() -> pd.DataFrame:
    """Load home team data from database using batch query.

    Returns:
        DataFrame with home team player data
    """
    team_names: list[str] = st.session_state.get("home_team", [])
    if not team_names:
        return pd.DataFrame(columns=PLAYER_COLUMNS)

    try:
        with get_connection() as conn:
            # Single batch query instead of N+1 queries
            df = get_players_by_full_names(conn, team_names)
            st.session_state.home_team_df = df
            return df
    except DatabaseConnectionError as e:
        st.error("Could not connect to database. Please try again later.")
        logger.error(f"Database connection error: {e}")
        return pd.DataFrame(columns=PLAYER_COLUMNS)
    except QueryExecutionError as e:
        st.error("Error loading team data. Please try again.")
        logger.error(f"Query error: {e}")
        return pd.DataFrame(columns=PLAYER_COLUMNS)


# Load data
player_search = find_player(player_add)
home_team_df = find_home_team()

# Combine search results with current team
if not home_team_df.empty:
    name_list = home_team_df["FULL_NAME"].tolist()
    player_search = player_search + [n for n in name_list if n not in player_search]


def save_state() -> None:
    """Save the selected players to session state."""
    saved_players = home_team_df["FULL_NAME"].tolist() if not home_team_df.empty else []
    holder = saved_players + player_selected

    if len(player_selected) > len(saved_players):
        for player in holder:
            if player not in st.session_state.home_team:
                st.session_state.home_team.append(player)
    elif len(player_selected) < len(saved_players):
        for player in saved_players:
            if player not in player_selected:
                st.session_state.home_team.remove(player)
    st.rerun()


col1, col2 = st.columns([7, 1])
with col1:
    default_selection = home_team_df["FULL_NAME"].tolist() if not home_team_df.empty else []
    player_selected = st.multiselect(
        "Search Results:",
        player_search,
        default_selection,
        label_visibility="collapsed",
    )
with col2:
    if st.button("Save Team"):
        save_state()

safe_heading("Preview", level=1, color="steelblue")

st.dataframe(home_team_df)

radio_index: int = st.session_state.get("radio_index", 0)
col1, col2, col3, col4, col5 = st.columns(5)

with col3:
    safe_heading("Away Team", level=3, color="steelblue")
    difficulty = st.radio(
        label="Difficulty",
        index=radio_index,
        options=list(DIFFICULTY_PRESETS.keys()),
        label_visibility="collapsed",
    )

    if difficulty and difficulty in DIFFICULTY_PRESETS:
        st.session_state.away_stats = list(DIFFICULTY_PRESETS[difficulty])
        st.session_state.radio_index = list(DIFFICULTY_PRESETS.keys()).index(difficulty)
    else:
        st.write("You didn't select a difficulty.")
