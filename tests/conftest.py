"""Pytest fixtures for NBA Streamlit application tests."""

from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest


@pytest.fixture
def mock_snowflake_connection() -> MagicMock:
    """Create a mock Snowflake connection.

    Returns:
        Mock connection object that simulates Snowflake connection behavior
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return mock_conn


@pytest.fixture
def sample_player_data() -> list[tuple[Any, ...]]:
    """Create sample player data matching database schema.

    Returns:
        List of tuples with sample player data
    """
    return [
        (
            "LeBron James",  # FULL_NAME
            10141,  # AST
            1107,  # BLK
            5972,  # DREB
            2891,  # FG3A
            1043,  # FG3M
            0.361,  # FG3_PCT
            24856,  # FGA
            12621,  # FGM
            0.508,  # FG_PCT
            11067,  # FTA
            7938,  # FTM
            0.717,  # FT_PCT
            1421,  # GP
            1421,  # GS
            54218,  # MIN
            1663,  # OREB
            2159,  # PF
            39223,  # PTS
            10988,  # REB
            2219,  # STL
            5015,  # TOV
            "LeBron",  # FIRST_NAME
            "James",  # LAST_NAME
            "lebron james",  # FULL_NAME_LOWER
            "lebron",  # FIRST_NAME_LOWER
            "james",  # LAST_NAME_LOWER
            True,  # IS_ACTIVE
        ),
        (
            "Michael Jordan",
            5633,
            893,
            4578,
            1778,
            581,
            0.327,
            24537,
            12192,
            0.497,
            8772,
            7327,
            0.835,
            1072,
            1039,
            41011,
            1463,
            2783,
            32292,
            6672,
            2514,
            2924,
            "Michael",
            "Jordan",
            "michael jordan",
            "michael",
            "jordan",
            False,
        ),
    ]


@pytest.fixture
def sample_player_df(sample_player_data: list[tuple]) -> pd.DataFrame:
    """Create sample player DataFrame.

    Args:
        sample_player_data: List of player tuples

    Returns:
        DataFrame with sample player data
    """
    from src.config import PLAYER_COLUMNS

    return pd.DataFrame(sample_player_data, columns=PLAYER_COLUMNS)


@pytest.fixture
def sample_team_stats() -> list[list[float]]:
    """Create sample team stats for ML model input.

    Returns:
        List of player stat lists (5 players x 10 stats)
    """
    return [
        [1500.0, 100.0, 200.0, 300.0, 50.0, 30.0, 100.0, 0.35, 0.80, 500.0],
        [1200.0, 80.0, 180.0, 250.0, 40.0, 25.0, 90.0, 0.38, 0.75, 450.0],
        [1000.0, 60.0, 150.0, 200.0, 35.0, 20.0, 80.0, 0.40, 0.82, 400.0],
        [800.0, 50.0, 120.0, 150.0, 30.0, 15.0, 70.0, 0.33, 0.78, 350.0],
        [600.0, 40.0, 100.0, 100.0, 25.0, 10.0, 60.0, 0.36, 0.85, 300.0],
    ]
