"""Local CSV data management with error handling."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger("streamlit_nba")

# Resolve path relative to this module
CSV_PATH = Path(__file__).resolve().parent.parent.parent / "snowflake_nba.csv"


class DatabaseConnectionError(Exception):
    """Raised when local data file cannot be found or loaded."""

    pass


class QueryExecutionError(Exception):
    """Raised when data query fails."""

    pass


def load_data() -> pd.DataFrame:
    """Load the local CSV data.

    Returns:
        DataFrame containing player data

    Raises:
        DatabaseConnectionError: If file cannot be loaded
    """
    if not CSV_PATH.exists():
        logger.error("Data file not found: %s", CSV_PATH)
        raise DatabaseConnectionError(f"Data file not found: {CSV_PATH}")

    try:
        df = pd.read_csv(CSV_PATH)
        # Ensure column names match expected Snowflake names (uppercase)
        df.columns = [col.upper() for col in df.columns]
        return df
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as e:
        logger.error("Failed to load CSV data: %s", e)
        msg = f"Could not load data from {CSV_PATH}: {e}"
        raise DatabaseConnectionError(msg) from e


def get_data() -> pd.DataFrame:
    """Get player data from the local CSV.

    Returns:
        DataFrame with player data

    Raises:
        DatabaseConnectionError: If data cannot be loaded
    """
    return load_data()
