"""Tests for Pydantic models."""

import pytest

from src.config import DIFFICULTY_PRESETS
from src.models.player import DifficultySettings


class TestDifficultySettings:
    """Tests for DifficultySettings model."""

    @pytest.mark.parametrize("preset_name", list(DIFFICULTY_PRESETS.keys()))
    def test_from_preset_valid(self, preset_name: str) -> None:
        """Test creating DifficultySettings from valid presets."""
        settings = DifficultySettings.from_preset(preset_name)

        assert settings.name == preset_name
        expected = DIFFICULTY_PRESETS[preset_name]
        assert settings.pts_threshold == expected[0]
        assert settings.reb_threshold == expected[1]
        assert settings.ast_threshold == expected[2]
        assert settings.stl_threshold == expected[3]

    def test_from_preset_invalid(self) -> None:
        """Test that invalid preset name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            DifficultySettings.from_preset("Invalid Preset")

        assert "Unknown difficulty preset" in str(exc_info.value)

    def test_as_tuple(self) -> None:
        """Test converting settings to tuple."""
        settings = DifficultySettings.from_preset("Regular")

        result = settings.as_tuple()

        assert result == DIFFICULTY_PRESETS["Regular"]
        assert isinstance(result, tuple)
        assert len(result) == 4

    def test_regular_preset_values(self) -> None:
        """Test Regular preset has expected values."""
        settings = DifficultySettings.from_preset("Regular")

        assert settings.pts_threshold == 850
        assert settings.reb_threshold == 400
        assert settings.ast_threshold == 200
        assert settings.stl_threshold == 60

    def test_dream_team_preset_values(self) -> None:
        """Test Dream Team preset has highest values."""
        settings = DifficultySettings.from_preset("Dream Team")

        assert settings.pts_threshold == 1450
        assert settings.reb_threshold == 700
        assert settings.ast_threshold == 500
        assert settings.stl_threshold == 120
