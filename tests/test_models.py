"""Tests for Pydantic models."""

import pytest

from src.config import DIFFICULTY_PRESETS
from src.models.player import DifficultySettings, PlayerStats


class TestPlayerStats:
    """Tests for PlayerStats model."""

    def test_from_db_row(self, sample_player_data: list) -> None:
        """Test creating PlayerStats from database row tuple."""
        row = sample_player_data[0]  # LeBron James data

        player = PlayerStats.from_db_row(row)

        assert player.full_name == "LeBron James"
        assert player.pts == 39223
        assert player.ast == 10141
        assert player.is_active is True

    def test_validates_negative_stats(self) -> None:
        """Test that negative stats are rejected."""
        with pytest.raises(ValueError):
            PlayerStats(
                full_name="Test Player",
                ast=-1,  # Invalid
                blk=0,
                dreb=0,
                fg3a=0,
                fg3m=0,
                fg3_pct=0.0,
                fga=0,
                fgm=0,
                fg_pct=0.0,
                fta=0,
                ftm=0,
                ft_pct=0.0,
                gp=0,
                gs=0,
                min=0,
                oreb=0,
                pf=0,
                pts=0,
                reb=0,
                stl=0,
                tov=0,
                first_name="Test",
                last_name="Player",
                full_name_lower="test player",
                first_name_lower="test",
                last_name_lower="player",
                is_active=True,
            )

    def test_validates_percentage_range(self) -> None:
        """Test that percentages must be 0-1."""
        with pytest.raises(ValueError):
            PlayerStats(
                full_name="Test Player",
                ast=0,
                blk=0,
                dreb=0,
                fg3a=0,
                fg3m=0,
                fg3_pct=1.5,  # Invalid - over 1.0
                fga=0,
                fgm=0,
                fg_pct=0.0,
                fta=0,
                ftm=0,
                ft_pct=0.0,
                gp=0,
                gs=0,
                min=0,
                oreb=0,
                pf=0,
                pts=0,
                reb=0,
                stl=0,
                tov=0,
                first_name="Test",
                last_name="Player",
                full_name_lower="test player",
                first_name_lower="test",
                last_name_lower="player",
                is_active=True,
            )


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
