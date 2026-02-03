"""Database module for connection management and queries."""

from src.database.connection import (
    DatabaseConnectionError,
    QueryExecutionError,
    get_connection,
)
from src.database.queries import (
    get_away_team_by_stats,
    get_player_by_full_name,
    get_players_by_full_names,
    search_player_by_name,
)

__all__ = [
    "DatabaseConnectionError",
    "QueryExecutionError",
    "get_away_team_by_stats",
    "get_connection",
    "get_player_by_full_name",
    "get_players_by_full_names",
    "search_player_by_name",
]
