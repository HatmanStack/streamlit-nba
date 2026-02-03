"""Tests for database module."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.config import MAX_QUERY_ATTEMPTS, PLAYER_COLUMNS
from src.database.connection import QueryExecutionError
from src.database.queries import (
    get_away_team_by_stats,
    get_player_by_full_name,
    get_players_by_full_names,
    search_player_by_name,
)


class TestSearchPlayerByName:
    """Tests for search_player_by_name function."""

    def test_uses_parameterized_query(
        self, mock_snowflake_connection: MagicMock
    ) -> None:
        """Verify parameterized queries are used (not string formatting)."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("LeBron James",)]
        mock_snowflake_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        search_player_by_name(mock_snowflake_connection, "james")

        # Verify execute was called with params tuple, not string formatting
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        # Query should use %s placeholders
        assert "%s" in query
        # Should not contain the actual search term in the query string
        assert "james" not in query.lower()
        # Params should be a tuple with the search term
        assert params == ("james", "james", "james")

    def test_returns_list_of_tuples(
        self, mock_snowflake_connection: MagicMock
    ) -> None:
        """Test that results are returned as list of tuples."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("LeBron James",),
            ("James Harden",),
        ]
        mock_snowflake_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        result = search_player_by_name(mock_snowflake_connection, "james")

        assert result == [("LeBron James",), ("James Harden",)]


class TestGetPlayersByFullNames:
    """Tests for get_players_by_full_names batch query."""

    def test_single_query_for_multiple_names(
        self, mock_snowflake_connection: MagicMock, sample_player_data: list
    ) -> None:
        """Verify batch query uses single IN clause instead of N queries."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = sample_player_data
        mock_snowflake_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        names = ["LeBron James", "Michael Jordan"]
        get_players_by_full_names(mock_snowflake_connection, names)

        # Should only execute one query
        assert mock_cursor.execute.call_count == 1

        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        # Query should have IN clause with placeholders
        assert "IN" in query.upper()
        assert "%s" in query
        # Params should be tuple of names
        assert params == ("LeBron James", "Michael Jordan")

    def test_returns_dataframe(
        self, mock_snowflake_connection: MagicMock, sample_player_data: list
    ) -> None:
        """Test that results are returned as DataFrame."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = sample_player_data
        mock_snowflake_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        result = get_players_by_full_names(
            mock_snowflake_connection, ["LeBron James", "Michael Jordan"]
        )

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == PLAYER_COLUMNS
        assert len(result) == 2

    def test_empty_names_returns_empty_dataframe(
        self, mock_snowflake_connection: MagicMock
    ) -> None:
        """Test that empty input returns empty DataFrame without query."""
        mock_cursor = MagicMock()
        mock_snowflake_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        result = get_players_by_full_names(mock_snowflake_connection, [])

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        # Should not execute any query
        mock_cursor.execute.assert_not_called()


class TestGetAwayTeamByStats:
    """Tests for get_away_team_by_stats with max_attempts guard."""

    def test_max_attempts_raises_error(
        self, mock_snowflake_connection: MagicMock
    ) -> None:
        """Test that max_attempts limit prevents infinite loop."""
        mock_cursor = MagicMock()
        # Always return wrong number of players
        mock_cursor.fetchall.return_value = [("Player1",), ("Player2",)]
        mock_snowflake_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        with pytest.raises(QueryExecutionError) as exc_info:
            get_away_team_by_stats(
                mock_snowflake_connection,
                pts_threshold=1000,
                reb_threshold=500,
                ast_threshold=300,
                stl_threshold=100,
                max_attempts=3,
            )

        assert "3 attempts" in str(exc_info.value)
        assert mock_cursor.execute.call_count == 3

    def test_success_on_first_try(
        self, mock_snowflake_connection: MagicMock, sample_player_data: list
    ) -> None:
        """Test successful query on first attempt."""
        mock_cursor = MagicMock()
        # Return exactly 5 players
        mock_cursor.fetchall.return_value = sample_player_data * 3  # 6 players
        mock_cursor.fetchall.return_value = [
            sample_player_data[0],
            sample_player_data[1],
            sample_player_data[0],
            sample_player_data[1],
            sample_player_data[0],
        ]
        mock_snowflake_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        result = get_away_team_by_stats(
            mock_snowflake_connection,
            pts_threshold=1000,
            reb_threshold=500,
            ast_threshold=300,
            stl_threshold=100,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        # Should only need one query
        assert mock_cursor.execute.call_count == 1

    def test_uses_parameterized_query(
        self, mock_snowflake_connection: MagicMock, sample_player_data: list
    ) -> None:
        """Verify parameterized queries are used for stat thresholds."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            sample_player_data[0],
            sample_player_data[1],
            sample_player_data[0],
            sample_player_data[1],
            sample_player_data[0],
        ]
        mock_snowflake_connection.cursor.return_value.__enter__.return_value = (
            mock_cursor
        )

        get_away_team_by_stats(
            mock_snowflake_connection,
            pts_threshold=1000,
            reb_threshold=500,
            ast_threshold=300,
            stl_threshold=100,
        )

        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        # Query should use %s placeholders
        assert "%s" in query
        # Should not contain actual numbers in query
        assert "1000" not in query
        assert "500" not in query
        # Params should be tuple of thresholds
        assert params == (1000, 500, 300, 100)
