"""Local CSV data management with error handling."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pandas as pd
import streamlit as st

logger = logging.getLogger("streamlit_nba")

CSV_PATH = Path("snowflake_nba.csv")


class DatabaseConnectionError(Exception):
    """Raised when local data file cannot be found or loaded."""

    pass


class QueryExecutionError(Exception):
    """Raised when data query fails."""

    pass


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the local CSV data.

    Returns:
        DataFrame containing player data

    Raises:
        DatabaseConnectionError: If file cannot be loaded
    """
    if not CSV_PATH.exists():
        logger.error(f"Data file not found: {CSV_PATH}")
        raise DatabaseConnectionError(f"Data file not found: {CSV_PATH}")

    try:
        df = pd.read_csv(CSV_PATH)
        # Ensure column names match expected Snowflake names (uppercase)
        df.columns = [col.upper() for col in df.columns]
        return df
    except Exception as e:
        logger.error(f"Failed to load CSV data: {e}")
        raise DatabaseConnectionError(f"Could not load data from {CSV_PATH}: {e}") from e


@contextmanager
def get_connection() -> Generator[pd.DataFrame, None, None]:
    """Context manager for local data access with error handling.

    Yields:
        DataFrame with player data

    Raises:
        DatabaseConnectionError: If data cannot be loaded
    """
    try:
        yield load_data()
    except DatabaseConnectionError as e:
        logger.error(f"Data access error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error accessing data: {e}")
        raise DatabaseConnectionError(f"Data access failed: {e}") from e
    finally:
        pass
