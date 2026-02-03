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
        home_stats = [[1.0, 2.0], [3.0, 4.0]]  # 2 players, 2 stats each
        away_stats = [[5.0, 6.0], [7.0, 8.0]]

        home_array, away_array, combined = analyze_team_stats(
            home_stats, away_stats
        )

        # Home should be first 4 values, away next 4
        np.testing.assert_array_equal(
            combined[0], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        )


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
    """Tests for get_winner_model caching."""

    @patch("src.ml.model.load_model")
    @patch("src.ml.model.Path")
    def test_raises_error_for_missing_model(
        self, mock_path: MagicMock, mock_load: MagicMock
    ) -> None:
        """Test that missing model file raises ModelLoadError."""
        from src.ml.model import get_winner_model

        # Clear the cache to ensure fresh test
        get_winner_model.clear()

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        with pytest.raises(ModelLoadError) as exc_info:
            get_winner_model("nonexistent.keras")

        assert "not found" in str(exc_info.value)
