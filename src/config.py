"""Application configuration, constants, and logging setup."""

import logging
from typing import Final

# Database column names for player data
PLAYER_COLUMNS: Final[list[str]] = [
    "FULL_NAME",
    "AST",
    "BLK",
    "DREB",
    "FG3A",
    "FG3M",
    "FG3_PCT",
    "FGA",
    "FGM",
    "FG_PCT",
    "FTA",
    "FTM",
    "FT_PCT",
    "GP",
    "GS",
    "MIN",
    "OREB",
    "PF",
    "PTS",
    "REB",
    "STL",
    "TOV",
    "FIRST_NAME",
    "LAST_NAME",
    "FULL_NAME_LOWER",
    "FIRST_NAME_LOWER",
    "LAST_NAME_LOWER",
    "IS_ACTIVE",
]

# Columns used for ML model features
STAT_COLUMNS: Final[list[str]] = [
    "PTS",
    "OREB",
    "DREB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "FG3_PCT",
    "FT_PCT",
    "FGM",
]

# Game configuration
TEAM_SIZE: Final[int] = 5
MAX_QUERY_ATTEMPTS: Final[int] = 10

# Difficulty presets: (PTS, REB, AST, STL)
DIFFICULTY_PRESETS: Final[dict[str, tuple[int, int, int, int]]] = {
    "Regular": (850, 400, 200, 60),
    "93' Bulls": (1050, 500, 300, 80),
    "All-Stars": (1250, 600, 400, 100),
    "Dream Team": (1450, 700, 500, 120),
}

# Score ranges for game simulation
WINNER_SCORE_RANGE: Final[tuple[int, int]] = (90, 130)
LOSER_SCORE_RANGE: Final[tuple[int, int]] = (80, 120)

# Default fallback scores when generation fails
DEFAULT_WINNER_SCORE: Final[int] = 100
DEFAULT_LOSER_SCORE: Final[int] = 90


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the application logger.

    Args:
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("streamlit_nba")
    logger.setLevel(level)
    return logger


# Module-level logger instance
logger: Final[logging.Logger] = setup_logging()
