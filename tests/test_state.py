"""Tests for session state management functions."""

from unittest.mock import patch

import pandas as pd

from src.config import DIFFICULTY_PRESETS


class TestInitSessionState:
    """Tests for init_session_state."""

    def test_initializes_all_expected_keys(self) -> None:
        """Verify all default keys are created."""
        state: dict = {}
        with patch("src.state.session.st") as mock_st:
            mock_st.session_state = state
            from src.state.session import init_session_state

            init_session_state()

        expected_keys = {
            "home_team",
            "away_team",
            "away_team_df",
            "away_stats",
            "home_team_df",
            "radio_index",
        }
        assert set(state.keys()) == expected_keys

    def test_does_not_overwrite_existing_values(self) -> None:
        """Verify calling init twice does not overwrite existing values."""
        state: dict = {"home_team": ["Player A"]}
        with patch("src.state.session.st") as mock_st:
            mock_st.session_state = state
            from src.state.session import init_session_state

            init_session_state()

        assert state["home_team"] == ["Player A"]

    def test_sets_correct_default_away_stats(self) -> None:
        """Verify away_stats defaults to Regular difficulty preset."""
        state: dict = {}
        with patch("src.state.session.st") as mock_st:
            mock_st.session_state = state
            from src.state.session import init_session_state

            init_session_state()

        assert state["away_stats"] == list(DIFFICULTY_PRESETS["Regular"])

    def test_sets_empty_dataframes_by_default(self) -> None:
        """Verify DataFrames start empty."""
        state: dict = {}
        with patch("src.state.session.st") as mock_st:
            mock_st.session_state = state
            from src.state.session import init_session_state

            init_session_state()

        assert isinstance(state["away_team_df"], pd.DataFrame)
        assert state["away_team_df"].empty
        assert isinstance(state["home_team_df"], pd.DataFrame)
        assert state["home_team_df"].empty


class TestGetAwayStats:
    """Tests for get_away_stats."""

    def test_returns_stats_from_session(self) -> None:
        """Verify returns stats when properly set in session."""
        state: dict = {"away_stats": [100, 200, 300, 400]}
        with patch("src.state.session.st") as mock_st:
            mock_st.session_state = state
            from src.state.session import get_away_stats

            result = get_away_stats()

        assert result == [100, 200, 300, 400]

    def test_returns_defaults_when_invalid(self) -> None:
        """Verify returns defaults when away_stats is invalid."""
        state: dict = {"away_stats": "invalid"}
        with patch("src.state.session.st") as mock_st:
            mock_st.session_state = state
            from src.state.session import get_away_stats

            result = get_away_stats()

        assert result == list(DIFFICULTY_PRESETS["Regular"])


class TestGetHomeTeamDf:
    """Tests for get_home_team_df."""

    def test_returns_dataframe_from_session(self) -> None:
        """Verify returns DataFrame when set in session."""
        expected_df = pd.DataFrame({"FULL_NAME": ["Player A"]})
        state: dict = {"home_team_df": expected_df}
        with patch("src.state.session.st") as mock_st:
            mock_st.session_state = state
            from src.state.session import get_home_team_df

            result = get_home_team_df()

        pd.testing.assert_frame_equal(result, expected_df)

    def test_returns_empty_dataframe_when_not_set(self) -> None:
        """Verify returns empty DataFrame when not set."""
        state: dict = {}
        with patch("src.state.session.st") as mock_st:
            mock_st.session_state = state
            from src.state.session import get_home_team_df

            result = get_home_team_df()

        assert isinstance(result, pd.DataFrame)
        assert result.empty
