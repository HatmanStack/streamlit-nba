"""Game play page with prediction and scoring."""

import logging
import random

import pandas as pd
import streamlit as st

from src.config import (
    DEFAULT_LOSER_SCORE,
    DEFAULT_WINNER_SCORE,
    LOSER_SCORE_RANGE,
    MAX_QUERY_ATTEMPTS,
    STAT_COLUMNS,
    TEAM_SIZE,
    WINNER_SCORE_RANGE,
)
from src.database.connection import (
    DatabaseConnectionError,
    QueryExecutionError,
    get_connection,
)
from src.database.queries import get_away_team_by_stats
from src.ml.model import ModelLoadError, analyze_team_stats, predict_winner
from src.state.session import get_away_stats, get_home_team_df, init_session_state
from src.utils.html import safe_heading

logger = logging.getLogger("streamlit_nba")


def on_page_load() -> None:
    """Configure page settings."""
    st.set_page_config(layout="wide")


on_page_load()

# Initialize session state BEFORE any access
init_session_state()

# Get stats safely with fallback
stats = get_away_stats()
teams_good = True


def find_away_team(stat_thresholds: list[int]) -> pd.DataFrame:
    """Generate away team based on difficulty stats.

    Args:
        stat_thresholds: List of [pts, reb, ast, stl] thresholds

    Returns:
        DataFrame with away team data, or empty DataFrame on error
    """
    try:
        with get_connection() as conn:
            return get_away_team_by_stats(
                conn,
                pts_threshold=stat_thresholds[0],
                reb_threshold=stat_thresholds[1],
                ast_threshold=stat_thresholds[2],
                stl_threshold=stat_thresholds[3],
                max_attempts=MAX_QUERY_ATTEMPTS,
            )
    except DatabaseConnectionError as e:
        st.error("Could not connect to database. Please try again later.")
        logger.error(f"Database connection error: {e}")
        return pd.DataFrame()
    except QueryExecutionError as e:
        st.error("Could not generate away team. Please try again.")
        logger.error(f"Query error: {e}")
        return pd.DataFrame()


def get_score_board(final_score: int) -> list[int]:
    """Generate quarter-by-quarter scores that sum to final score.

    Args:
        final_score: Total game score

    Returns:
        List of [Q1, Q2, Q3, Q4, Final] scores
    """
    quarter_score = final_score // 4
    scores = [
        quarter_score + random.randint(-7, 7),
        quarter_score + random.randint(-3, 3),
        quarter_score + random.randint(-8, 8),
    ]
    # Q4 makes up the difference to hit exact final
    scores.append(final_score - sum(scores))
    scores.append(final_score)
    return scores


def generate_game_scores() -> tuple[int, int]:
    """Generate winner and loser scores with loop guard.

    Returns:
        Tuple of (winner_score, loser_score)
    """
    for _ in range(MAX_QUERY_ATTEMPTS):
        winner_score = random.randint(*WINNER_SCORE_RANGE)
        loser_score = random.randint(*LOSER_SCORE_RANGE)
        if winner_score > loser_score:
            return winner_score, loser_score

    # Fallback to guaranteed valid scores
    logger.warning("Score generation fell back to defaults")
    return DEFAULT_WINNER_SCORE, DEFAULT_LOSER_SCORE


# Check if home team is valid
home_team_df = get_home_team_df()

if home_team_df.empty or home_team_df.shape[0] != TEAM_SIZE:
    safe_heading(
        f"Your Team Doesn't Have {TEAM_SIZE} Players",
        level=3,
        color="red",
    )
    st.session_state.away_team_df = pd.DataFrame()
    teams_good = False
    winner_label = ""
    box_score = pd.DataFrame()
else:
    # Only generate away team if we don't have one or it's empty
    if st.session_state.get("away_team_df") is None or st.session_state.away_team_df.empty:
        st.session_state.away_team_df = find_away_team(stats)

    away_data = st.session_state.away_team_df
    if away_data.empty:
        teams_good = False
        winner_label = ""
        box_score = pd.DataFrame()

# Run prediction if both teams are valid
if teams_good and not st.session_state.away_team_df.empty:
    try:
        # Extract stats for ML model
        home_stats = home_team_df[STAT_COLUMNS].values.tolist()
        away_stats_data = st.session_state.away_team_df[STAT_COLUMNS].values.tolist()

        # Prepare data and predict
        _, _, combined = analyze_team_stats(home_stats, away_stats_data)
        probability, prediction = predict_winner(combined)

        # Generate scores
        winner_score, loser_score = generate_game_scores()

        # Build scoreboard based on prediction
        if prediction == 1:
            score_data = [
                get_score_board(winner_score),
                get_score_board(loser_score),
            ]
            winner_label = "Winner"
        else:
            score_data = [
                get_score_board(loser_score),
                get_score_board(winner_score),
            ]
            winner_label = "Loser"

        box_score = pd.DataFrame(
            score_data,
            columns=["1", "2", "3", "4", "Final"],
            index=["Home Team", "Away Team"],
        )

        logger.info(f"Prediction: {probability:.4f}")

    except ModelLoadError as e:
        st.error("Could not load prediction model. Please contact support.")
        logger.error(f"Model load error: {e}")
        teams_good = False
        winner_label = ""
        box_score = pd.DataFrame()
    except ValueError as e:
        st.error("Error processing team stats. Please try again.")
        logger.error(f"Stats processing error: {e}")
        teams_good = False
        winner_label = ""
        box_score = pd.DataFrame()

# Display results
safe_heading("Home Team", level=1, color="steelblue")
st.dataframe(home_team_df)

if teams_good and winner_label:
    logger.info("Teams Good")
    safe_heading(winner_label, level=3, color="steelblue")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.dataframe(box_score)

safe_heading("Away Team", level=1, color="steelblue")
st.dataframe(st.session_state.away_team_df)

def play_new_team() -> None:
    """Clear cached away team and rerun."""
    logger.info("New Team requested")
    st.session_state.away_team_df = pd.DataFrame()

st.button("Play New Team", on_click=play_new_team)
