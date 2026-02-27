"""Tests for database module using local pandas data."""

import pandas as pd
import pytest

from src.config import PLAYER_COLUMNS
from src.database.connection import QueryExecutionError
from src.database.queries import (
    get_away_team_by_stats,
    get_players_by_full_names,
    search_player_by_name,
)


class TestSearchPlayerByName:
    """Tests for search_player_by_name function."""

    def test_search_by_full_name(self, sample_player_df: pd.DataFrame) -> None:
        """Verify search finds player by full name."""
        result = search_player_by_name(sample_player_df, "LeBron James")
        assert result == [("LeBron James",)]

    def test_search_by_first_name(self, sample_player_df: pd.DataFrame) -> None:
        """Verify search finds player by first name."""
        result = search_player_by_name(sample_player_df, "LeBron")
        assert result == [("LeBron James",)]

    def test_search_by_last_name(self, sample_player_df: pd.DataFrame) -> None:
        """Verify search finds player by last name."""
        result = search_player_by_name(sample_player_df, "Jordan")
        assert result == [("Michael Jordan",)]

    def test_search_case_insensitive(self, sample_player_df: pd.DataFrame) -> None:
        """Verify search is case-insensitive."""
        result = search_player_by_name(sample_player_df, "lebron")
        assert result == [("LeBron James",)]

    def test_search_partial_name(self, sample_player_df: pd.DataFrame) -> None:
        """Verify search finds player by partial name."""
        result = search_player_by_name(sample_player_df, "Jord")
        assert result == [("Michael Jordan",)]

    def test_returns_empty_on_no_match(self, sample_player_df: pd.DataFrame) -> None:
        """Verify empty list returned when no player found."""
        result = search_player_by_name(sample_player_df, "NonExistent Player")
        assert result == []


class TestGetPlayersByFullNames:
    """Tests for get_players_by_full_names batch query."""

    def test_returns_correct_players(self, sample_player_df: pd.DataFrame) -> None:
        """Verify correct players are returned in DataFrame."""
        names = ["LeBron James", "Michael Jordan"]
        result = get_players_by_full_names(sample_player_df, names)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert set(result["FULL_NAME"]) == set(names)
        assert list(result.columns) == PLAYER_COLUMNS

    def test_empty_names_returns_empty_dataframe(
        self, sample_player_df: pd.DataFrame
    ) -> None:
        """Test that empty input returns empty DataFrame."""
        result = get_players_by_full_names(sample_player_df, [])

        assert isinstance(result, pd.DataFrame)
        assert result.empty
        assert list(result.columns) == PLAYER_COLUMNS


class TestGetAwayTeamByStats:
    """Tests for get_away_team_by_stats."""

    def test_max_attempts_raises_error(self) -> None:
        """Test that max_attempts limit works when population is too small."""
        # Create a DF with only 2 players
        df = pd.DataFrame([
            {"FULL_NAME": "P1", "PTS": 1001, "REB": 501, "AST": 301, "STL": 101},
            {"FULL_NAME": "P2", "PTS": 1001, "REB": 501, "AST": 301, "STL": 101},
        ])
        # Add missing columns to avoid errors if needed, though queries only use these
        for col in PLAYER_COLUMNS:
            if col not in df.columns:
                df[col] = 0

        with pytest.raises(QueryExecutionError) as exc_info:
            get_away_team_by_stats(
                df,
                pts_threshold=1000,
                reb_threshold=500,
                ast_threshold=300,
                stl_threshold=100,
                max_attempts=3,
            )

        assert "3 attempts" in str(exc_info.value)

    def test_success_with_enough_players(self) -> None:
        """Test successful generation with sufficient population."""
        # Create a DF with 10 players meeting criteria
        data = []
        for i in range(10):
            data.append({
                "FULL_NAME": f"Player{i}",
                "PTS": 2000, "REB": 1000, "AST": 500, "STL": 200
            })
        df = pd.DataFrame(data)
        for col in PLAYER_COLUMNS:
            if col not in df.columns:
                df[col] = 0

        result = get_away_team_by_stats(
            df,
            pts_threshold=1000,
            reb_threshold=500,
            ast_threshold=300,
            stl_threshold=100,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
