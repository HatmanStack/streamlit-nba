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

    Ensures 5 unique players are selected who meet various stat criteria.

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
        QueryExecutionError: If unable to get 5 players within max_attempts
    """
    # Pre-filter pools to improve performance and reliability
    pool_pts = df[df["PTS"] > pts_threshold]
    pool_reb = df[df["REB"] > reb_threshold]
    pool_ast = df[df["AST"] > ast_threshold]
    pool_stl = df[df["STL"] > stl_threshold]

    for attempt in range(max_attempts):
        try:
            # We need 5 unique players. Strategy:
            # 1. Pick 2 from PTS
            # 2. Pick 1 from REB (not in PTS)
            # 3. Pick 1 from AST (not in PTS or REB)
            # 4. Pick 1 from STL (not in PTS, REB, or AST)

            selected_indices: set[int] = set()

            # Step 1: PTS (2 players)
            if len(pool_pts) < 2:
                raise ValueError("PTS pool too small")
            p12 = pool_pts.sample(n=2, replace=False)
            selected_indices.update(p12.index.tolist())

            # Step 2: REB (1 player)
            remaining_reb = pool_reb[~pool_reb.index.isin(selected_indices)]
            if remaining_reb.empty:
                raise ValueError("REB pool exhausted")
            p3 = remaining_reb.sample(n=1)
            selected_indices.update(p3.index.tolist())

            # Step 3: AST (1 player)
            remaining_ast = pool_ast[~pool_ast.index.isin(selected_indices)]
            if remaining_ast.empty:
                raise ValueError("AST pool exhausted")
            p4 = remaining_ast.sample(n=1)
            selected_indices.update(p4.index.tolist())

            # Step 4: STL (1 player)
            remaining_stl = pool_stl[~pool_stl.index.isin(selected_indices)]
            if remaining_stl.empty:
                raise ValueError("STL pool exhausted")
            p5 = remaining_stl.sample(n=1)
            selected_indices.update(p5.index.tolist())

            results = df.loc[list(selected_indices)]
            if len(results) == 5:
                logger.info(f"Got away team on attempt {attempt + 1}")
                return results

        except ValueError as e:
            logger.debug(f"Attempt {attempt + 1} failed: {e}")
            continue

    raise QueryExecutionError(
        f"Could not generate away team with 5 players after {max_attempts} attempts. "
        "Try lowering the difficulty."
    )
