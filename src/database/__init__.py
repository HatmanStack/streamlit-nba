"""Database module for connection management and queries."""

from src.database.connection import (
    get_connection,
    DatabaseConnectionError,
    QueryExecutionError,
)
from src.database.queries import (
    search_player_by_name,
    get_player_by_full_name,
    get_players_by_full_names,
    get_away_team_by_stats,
)

__all__ = [
    "get_connection",
    "DatabaseConnectionError",
    "QueryExecutionError",
    "search_player_by_name",
    "get_player_by_full_name",
    "get_players_by_full_names",
    "get_away_team_by_stats",
]
