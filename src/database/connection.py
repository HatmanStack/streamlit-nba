"""Database connection management with error handling."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import snowflake.connector
import streamlit as st
from snowflake.connector import SnowflakeConnection
from snowflake.connector.errors import DatabaseError, ProgrammingError

logger = logging.getLogger("streamlit_nba")


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""

    pass


class QueryExecutionError(Exception):
    """Raised when query execution fails."""

    pass


@st.cache_resource
def _get_connection_pool() -> SnowflakeConnection:
    """Create and cache a Snowflake connection.

    Returns:
        Cached Snowflake connection

    Raises:
        DatabaseConnectionError: If connection cannot be established
    """
    try:
        return snowflake.connector.connect(**st.secrets["snowflake"])
    except DatabaseError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise DatabaseConnectionError(f"Could not connect to database: {e}") from e
    except KeyError as e:
        logger.error("Snowflake credentials not found in secrets")
        raise DatabaseConnectionError(
            "Database credentials not configured. Please check st.secrets."
        ) from e


@contextmanager
def get_connection() -> Generator[SnowflakeConnection, None, None]:
    """Context manager for database connections with error handling.

    Yields:
        Active Snowflake connection

    Raises:
        DatabaseConnectionError: If connection fails

    Example:
        with get_connection() as conn:
            # use connection
    """
    try:
        conn = snowflake.connector.connect(**st.secrets["snowflake"])
        yield conn
    except DatabaseError as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseConnectionError(f"Database connection failed: {e}") from e
    except KeyError as e:
        logger.error("Snowflake credentials not found in secrets")
        raise DatabaseConnectionError(
            "Database credentials not configured. Please check st.secrets."
        ) from e
    finally:
        try:
            conn.close()
        except Exception:
            pass  # Connection may already be closed


def execute_query(
    conn: SnowflakeConnection,
    query: str,
    params: tuple[Any, ...] | list[Any] | None = None,
) -> list[tuple[Any, ...]]:
    """Execute a parameterized query safely.

    Args:
        conn: Active database connection
        query: SQL query with %s placeholders
        params: Query parameters (optional)

    Returns:
        List of result tuples

    Raises:
        QueryExecutionError: If query execution fails
    """
    try:
        with conn.cursor() as cur:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            return cur.fetchall()
    except ProgrammingError as e:
        logger.error(f"Query execution error: {e}")
        raise QueryExecutionError(f"Query failed: {e}") from e
    except DatabaseError as e:
        logger.error(f"Database error during query: {e}")
        raise QueryExecutionError(f"Database error: {e}") from e
