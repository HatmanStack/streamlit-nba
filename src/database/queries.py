"""Parameterized database queries for player data."""

import logging
from typing import Any

import pandas as pd
from snowflake.connector import SnowflakeConnection

from src.config import MAX_QUERY_ATTEMPTS, PLAYER_COLUMNS
from src.database.connection import QueryExecutionError, execute_query

logger = logging.getLogger("streamlit_nba")


def search_player_by_name(conn: SnowflakeConnection, name: str) -> list[tuple[str]]:
    """Search for players by name (first, last, or full name).

    Args:
        conn: Active database connection
        name: Search term (case-insensitive)

    Returns:
        List of tuples containing matching full names
    """
    name_lower = name.lower().strip()
    query = """
        SELECT full_name FROM NBA
        WHERE full_name_lower = %s
           OR first_name_lower = %s
           OR last_name_lower = %s
    """
    return execute_query(conn, query, (name_lower, name_lower, name_lower))


def get_player_by_full_name(
    conn: SnowflakeConnection, full_name: str
) -> tuple[Any, ...] | None:
    """Get a single player's full record by exact name match.

    Args:
        conn: Active database connection
        full_name: Exact full name of player

    Returns:
        Player data tuple or None if not found
    """
    query = "SELECT * FROM NBA WHERE FULL_NAME = %s"
    results = execute_query(conn, query, (full_name,))
    return results[0] if results else None


def get_players_by_full_names(
    conn: SnowflakeConnection, names: list[str]
) -> pd.DataFrame:
    """Get multiple players' records in a single batch query.

    This fixes the N+1 query problem by using a single IN clause
    instead of multiple individual queries.

    Args:
        conn: Active database connection
        names: List of exact full names

    Returns:
        DataFrame with player data
    """
    if not names:
        return pd.DataFrame(columns=PLAYER_COLUMNS)

    # Build parameterized IN clause
    placeholders = ", ".join(["%s"] * len(names))
    query = f"SELECT * FROM NBA WHERE FULL_NAME IN ({placeholders})"

    results = execute_query(conn, query, tuple(names))
    return pd.DataFrame(results, columns=PLAYER_COLUMNS)


def get_away_team_by_stats(
    conn: SnowflakeConnection,
    pts_threshold: int,
    reb_threshold: int,
    ast_threshold: int,
    stl_threshold: int,
    max_attempts: int = MAX_QUERY_ATTEMPTS,
) -> pd.DataFrame:
    """Get a random away team based on stat thresholds.

    Uses UNION with SAMPLE to get diverse players meeting stat criteria.
    Includes a max_attempts guard to prevent infinite loops.

    Args:
        conn: Active database connection
        pts_threshold: Minimum career points
        reb_threshold: Minimum career rebounds
        ast_threshold: Minimum career assists
        stl_threshold: Minimum career steals
        max_attempts: Maximum query attempts before raising error

    Returns:
        DataFrame with 5 players

    Raises:
        QueryExecutionError: If unable to get 5 players within max_attempts
    """
    query = """
        SELECT * FROM (SELECT * FROM NBA WHERE PTS > %s) SAMPLE (2 ROWS)
        UNION
        SELECT * FROM (SELECT * FROM NBA WHERE REB > %s) SAMPLE (1 ROWS)
        UNION
        SELECT * FROM (SELECT * FROM NBA WHERE AST > %s) SAMPLE (1 ROWS)
        UNION
        SELECT * FROM (SELECT * FROM NBA WHERE STL > %s) SAMPLE (1 ROWS)
    """
    params = (pts_threshold, reb_threshold, ast_threshold, stl_threshold)

    for attempt in range(max_attempts):
        results = execute_query(conn, query, params)
        if len(results) == 5:
            logger.info(f"Got away team on attempt {attempt + 1}")
            return pd.DataFrame(results, columns=PLAYER_COLUMNS)
        logger.debug(f"Attempt {attempt + 1}: got {len(results)} players, need 5")

    # Fallback: if we can't get exactly 5, raise an error
    raise QueryExecutionError(
        f"Could not generate away team with 5 players after {max_attempts} attempts. "
        f"Last attempt returned {len(results)} players."
    )
