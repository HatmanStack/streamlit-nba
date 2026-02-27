"""Local data queries using pandas on loaded CSV data."""

import logging
from typing import Any

import pandas as pd

from src.config import MAX_QUERY_ATTEMPTS, PLAYER_COLUMNS
from src.database.connection import QueryExecutionError

logger = logging.getLogger("streamlit_nba")


def search_player_by_name(df: pd.DataFrame, name: str) -> list[tuple[str]]:
    """Search for players by name (first, last, or full name).

    Args:
        df: Player DataFrame
        name: Search term (case-insensitive)

    Returns:
        List of tuples containing matching full names
    """
    name_lower = name.lower().strip()
    mask = (
        (df["FULL_NAME_LOWER"] == name_lower)
        | (df["FIRST_NAME_LOWER"] == name_lower)
        | (df["LAST_NAME_LOWER"] == name_lower)
    )
    results = df[mask]["FULL_NAME"].unique().tolist()
    return [(name,) for name in results]


def get_player_by_full_name(
    df: pd.DataFrame, full_name: str
) -> tuple[Any, ...] | None:
    """Get a single player's full record by exact name match.

    Args:
        df: Player DataFrame
        full_name: Exact full name of player

    Returns:
        Player data tuple or None if not found
    """
    result = df[df["FULL_NAME"] == full_name]
    if result.empty:
        return None
    return tuple(result.iloc[0].values)


def get_players_by_full_names(
    df: pd.DataFrame, names: list[str]
) -> pd.DataFrame:
    """Get multiple players' records in a single batch query.

    Args:
        df: Player DataFrame
        names: List of exact full names

    Returns:
        DataFrame with player data
    """
    if not names:
        return pd.DataFrame(columns=PLAYER_COLUMNS)

    return df[df["FULL_NAME"].isin(names)]


def get_away_team_by_stats(
    df: pd.DataFrame,
    pts_threshold: int,
    reb_threshold: int,
    ast_threshold: int,
    stl_threshold: int,
    max_attempts: int = MAX_QUERY_ATTEMPTS,
) -> pd.DataFrame:
    """Get a random away team based on stat thresholds.

    Replicates Snowflake's SAMPLE and UNION logic using pandas.

    Args:
        df: Player DataFrame
        pts_threshold: Minimum career points
        reb_threshold: Minimum career rebounds
        ast_threshold: Minimum career assists
        stl_threshold: Minimum career steals
        max_attempts: Maximum query attempts before raising error

    Returns:
        DataFrame with 5 players

    Raises:
        RuntimeError: If unable to get 5 players within max_attempts
    """
    for attempt in range(max_attempts):
        try:
            df1 = df[df["PTS"] > pts_threshold].sample(n=2)
            df2 = df[df["REB"] > reb_threshold].sample(n=1)
            df3 = df[df["AST"] > ast_threshold].sample(n=1)
            df4 = df[df["STL"] > stl_threshold].sample(n=1)

            results = pd.concat([df1, df2, df3, df4]).drop_duplicates()

            if len(results) == 5:
                logger.info(f"Got away team on attempt {attempt + 1}")
                return results
        except ValueError:
            # sample() can raise ValueError if n > population
            logger.debug(f"Attempt {attempt + 1}: stat thresholds too restrictive")
            continue

    raise QueryExecutionError(
        f"Could not generate away team with 5 players after {max_attempts} attempts. "
        "Try lowering the difficulty."
    )
