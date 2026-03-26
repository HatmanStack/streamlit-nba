"""Pydantic models for game data."""

from typing import ClassVar

from pydantic import BaseModel, Field, field_validator

from src.config import DIFFICULTY_PRESETS


class DifficultySettings(BaseModel):
    """Model for game difficulty settings."""

    VALID_PRESETS: ClassVar[set[str]] = set(DIFFICULTY_PRESETS.keys())

    name: str = Field(..., min_length=1)
    pts_threshold: int = Field(..., ge=0, description="Minimum career points")
    reb_threshold: int = Field(..., ge=0, description="Minimum career rebounds")
    ast_threshold: int = Field(..., ge=0, description="Minimum career assists")
    stl_threshold: int = Field(..., ge=0, description="Minimum career steals")

    @field_validator("name")
    @classmethod
    def validate_preset_name(cls, v: str) -> str:
        """Validate that preset name is recognized."""
        if v not in cls.VALID_PRESETS:
            raise ValueError(
                f"Unknown difficulty preset: {v}. "
                f"Valid options: {', '.join(sorted(cls.VALID_PRESETS))}"
            )
        return v

    @classmethod
    def from_preset(cls, preset_name: str) -> "DifficultySettings":
        """Create DifficultySettings from a named preset.

        Args:
            preset_name: Name of difficulty preset (e.g., "Regular", "Dream Team")

        Returns:
            DifficultySettings instance

        Raises:
            ValueError: If preset_name is not valid
        """
        if preset_name not in DIFFICULTY_PRESETS:
            raise ValueError(
                f"Unknown difficulty preset: {preset_name}. "
                f"Valid options: {', '.join(sorted(DIFFICULTY_PRESETS.keys()))}"
            )
        pts, reb, ast, stl = DIFFICULTY_PRESETS[preset_name]
        return cls(
            name=preset_name,
            pts_threshold=pts,
            reb_threshold=reb,
            ast_threshold=ast,
            stl_threshold=stl,
        )

    def as_tuple(self) -> tuple[int, int, int, int]:
        """Return thresholds as tuple for backward compatibility.

        Returns:
            Tuple of (pts, reb, ast, stl) thresholds
        """
        return (
            self.pts_threshold,
            self.reb_threshold,
            self.ast_threshold,
            self.stl_threshold,
        )
