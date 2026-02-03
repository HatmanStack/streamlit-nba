"""Pydantic models for player and game data."""

from typing import Any, ClassVar

from pydantic import BaseModel, Field, field_validator

from src.config import DIFFICULTY_PRESETS


class PlayerStats(BaseModel):
    """Model representing a player's career statistics."""

    full_name: str = Field(..., min_length=1, max_length=100)
    ast: int = Field(..., ge=0, description="Career assists")
    blk: int = Field(..., ge=0, description="Career blocks")
    dreb: int = Field(..., ge=0, description="Career defensive rebounds")
    fg3a: int = Field(..., ge=0, description="Career 3-point attempts")
    fg3m: int = Field(..., ge=0, description="Career 3-pointers made")
    fg3_pct: float = Field(..., ge=0.0, le=1.0, description="3-point percentage")
    fga: int = Field(..., ge=0, description="Career field goal attempts")
    fgm: int = Field(..., ge=0, description="Career field goals made")
    fg_pct: float = Field(..., ge=0.0, le=1.0, description="Field goal percentage")
    fta: int = Field(..., ge=0, description="Career free throw attempts")
    ftm: int = Field(..., ge=0, description="Career free throws made")
    ft_pct: float = Field(..., ge=0.0, le=1.0, description="Free throw percentage")
    gp: int = Field(..., ge=0, description="Games played")
    gs: int = Field(..., ge=0, description="Games started")
    min: int = Field(..., ge=0, description="Career minutes")
    oreb: int = Field(..., ge=0, description="Career offensive rebounds")
    pf: int = Field(..., ge=0, description="Career personal fouls")
    pts: int = Field(..., ge=0, description="Career points")
    reb: int = Field(..., ge=0, description="Career rebounds")
    stl: int = Field(..., ge=0, description="Career steals")
    tov: int = Field(..., ge=0, description="Career turnovers")
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    full_name_lower: str = Field(..., max_length=100)
    first_name_lower: str = Field(..., max_length=50)
    last_name_lower: str = Field(..., max_length=50)
    is_active: bool = Field(default=False)

    @classmethod
    def from_db_row(cls, row: tuple[Any, ...]) -> "PlayerStats":
        """Create PlayerStats from a database row tuple.

        Args:
            row: Database row tuple in PLAYER_COLUMNS order

        Returns:
            PlayerStats instance
        """
        return cls(
            full_name=row[0],
            ast=row[1],
            blk=row[2],
            dreb=row[3],
            fg3a=row[4],
            fg3m=row[5],
            fg3_pct=row[6] or 0.0,
            fga=row[7],
            fgm=row[8],
            fg_pct=row[9] or 0.0,
            fta=row[10],
            ftm=row[11],
            ft_pct=row[12] or 0.0,
            gp=row[13],
            gs=row[14],
            min=row[15],
            oreb=row[16],
            pf=row[17],
            pts=row[18],
            reb=row[19],
            stl=row[20],
            tov=row[21],
            first_name=row[22],
            last_name=row[23],
            full_name_lower=row[24],
            first_name_lower=row[25],
            last_name_lower=row[26],
            is_active=bool(row[27]) if row[27] is not None else False,
        )


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
