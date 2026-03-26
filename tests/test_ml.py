"""Tests for ML model module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.ml.model import ModelLoadError, analyze_team_stats, predict_winner


class TestAnalyzeTeamStats:
    """Tests for analyze_team_stats function."""

    def test_flattens_stats_correctly(
        self, sample_team_stats: list[list[float]]
    ) -> None:
        """Test that team stats are flattened correctly."""
        home_array, away_array, combined = analyze_team_stats(
            sample_team_stats, sample_team_stats
        )

        # Each team has 5 players x 10 stats = 50 values
        assert home_array.shape == (1, 50)
        assert away_array.shape == (1, 50)
        # Combined has both teams = 100 values
        assert combined.shape == (1, 100)

    def test_combined_contains_both_teams(
        self, sample_team_stats: list[list[float]]
    ) -> None:
        """Test that combined array contains both teams' stats."""
        home_stats = [[float(i * 10 + j) for j in range(10)] for i in range(5)]
        away_stats = [[float(50 + i * 10 + j) for j in range(10)] for i in range(5)]

        _home_array, _away_array, combined = analyze_team_stats(
            home_stats, away_stats
        )

        # Combined should have 100 values: 50 home + 50 away
        assert combined.shape == (1, 100)
        # First value should be home[0][0], last should be away[4][9]
        assert combined[0][0] == 0.0
        assert combined[0][50] == 50.0


class TestAnalyzeTeamStatsValidation:
    """Tests for input shape validation in analyze_team_stats."""

    def test_wrong_number_of_home_players_raises_error(self) -> None:
        """Test that wrong number of home players raises ValueError."""
        home_stats = [[1.0] * 10 for _ in range(4)]  # 4 players instead of 5
        away_stats = [[1.0] * 10 for _ in range(5)]

        with pytest.raises(ValueError, match="Expected 5 players"):
            analyze_team_stats(home_stats, away_stats)

    def test_wrong_number_of_away_players_raises_error(self) -> None:
        """Test that wrong number of away players raises ValueError."""
        home_stats = [[1.0] * 10 for _ in range(5)]
        away_stats = [[1.0] * 10 for _ in range(6)]  # 6 players instead of 5

        with pytest.raises(ValueError, match="Expected 5 players"):
            analyze_team_stats(home_stats, away_stats)

    def test_wrong_stat_count_raises_error(self) -> None:
        """Test that wrong number of stats per player raises ValueError."""
        home_stats = [[1.0] * 10 for _ in range(5)]
        away_stats = [[1.0] * 10 for _ in range(4)] + [[1.0] * 9]  # player with 9 stats

        with pytest.raises(ValueError, match="stats, expected 10"):
            analyze_team_stats(home_stats, away_stats)

    def test_home_player_wrong_stat_count_raises_error(self) -> None:
        """Test that home player with wrong stat count raises ValueError."""
        home_stats = [[1.0] * 9] + [[1.0] * 10 for _ in range(4)]  # first player has 9
        away_stats = [[1.0] * 10 for _ in range(5)]

        with pytest.raises(ValueError, match="stats, expected 10"):
            analyze_team_stats(home_stats, away_stats)


class TestPredictWinner:
    """Tests for predict_winner function."""

    @patch("src.ml.model.get_winner_model")
    def test_returns_probability_and_prediction(
        self, mock_get_model: MagicMock
    ) -> None:
        """Test that function returns (probability, prediction) tuple."""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.75]])
        mock_get_model.return_value = mock_model

        stats = np.random.rand(1, 100)
        probability, prediction = predict_winner(stats)

        assert isinstance(probability, float)
        assert isinstance(prediction, int)
        assert 0.0 <= probability <= 1.0
        assert prediction in (0, 1)

    @patch("src.ml.model.get_winner_model")
    def test_high_probability_predicts_win(
        self, mock_get_model: MagicMock
    ) -> None:
        """Test that high probability (>0.5) predicts home win (1)."""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.8]])
        mock_get_model.return_value = mock_model

        stats = np.random.rand(1, 100)
        probability, prediction = predict_winner(stats)

        assert probability == 0.8
        assert prediction == 1

    @patch("src.ml.model.get_winner_model")
    def test_low_probability_predicts_loss(
        self, mock_get_model: MagicMock
    ) -> None:
        """Test that low probability (<0.5) predicts home loss (0)."""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.3]])
        mock_get_model.return_value = mock_model

        stats = np.random.rand(1, 100)
        probability, prediction = predict_winner(stats)

        assert probability == 0.3
        assert prediction == 0

    @patch("src.ml.model.get_winner_model")
    def test_invalid_shape_raises_error(
        self, mock_get_model: MagicMock
    ) -> None:
        """Test that invalid input shape raises ValueError."""
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model

        # Wrong shape
        stats = np.random.rand(1, 50)

        with pytest.raises(ValueError) as exc_info:
            predict_winner(stats)

        assert "Expected input shape (1, 100)" in str(exc_info.value)

    @patch("src.ml.model.get_winner_model")
    def test_model_called_with_verbose_zero(
        self, mock_get_model: MagicMock
    ) -> None:
        """Test that model.predict is called with verbose=0."""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.5]])
        mock_get_model.return_value = mock_model

        stats = np.random.rand(1, 100)
        predict_winner(stats)

        mock_model.predict.assert_called_once_with(stats, verbose=0)


class TestGetWinnerModel:
    """Tests for get_winner_model loading."""

    @patch("src.ml.model.load_model")
    @patch("src.ml.model.Path")
    def test_raises_error_for_missing_model(
        self, mock_path: MagicMock, mock_load: MagicMock
    ) -> None:
        """Test that missing model file raises ModelLoadError."""
        from src.ml.model import get_winner_model

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        with pytest.raises(ModelLoadError) as exc_info:
            get_winner_model("nonexistent.keras")

        assert "not found" in str(exc_info.value)
