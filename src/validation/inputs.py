"""Input validation for user-provided data."""

import re

from pydantic import BaseModel, Field, field_validator

# Patterns that indicate SQL injection attempts
SQL_INJECTION_PATTERNS: list[str] = [
    r'[";]',  # Double quotes and semicolons (apostrophes allowed for names like O'Neal)
    r"--",  # SQL comment
    r"/\*",  # Block comment start
    r"\*/",  # Block comment end
    r"\bUNION\b",  # UNION keyword
    r"\bSELECT\b",  # SELECT keyword
    r"\bINSERT\b",  # INSERT keyword
    r"\bUPDATE\b",  # UPDATE keyword
    r"\bDELETE\b",  # DELETE keyword
    r"\bDROP\b",  # DROP keyword
    r"\bEXEC\b",  # EXEC keyword
    r"\bOR\s+\d+=\d+",  # OR 1=1 pattern
    r"\bAND\s+\d+=\d+",  # AND 1=1 pattern
    r"'\s*OR\s",  # ' OR pattern (SQL injection)
    r"'\s*AND\s",  # ' AND pattern (SQL injection)
]

# Compiled regex for efficiency
SQL_INJECTION_REGEX = re.compile(
    "|".join(SQL_INJECTION_PATTERNS), re.IGNORECASE
)


class PlayerSearchInput(BaseModel):
    """Validated player search input."""

    search_term: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Player name search term",
    )

    @field_validator("search_term")
    @classmethod
    def validate_no_sql_injection(cls, v: str) -> str:
        """Reject inputs containing SQL injection patterns.

        Args:
            v: Input search term

        Returns:
            Validated search term

        Raises:
            ValueError: If SQL injection pattern detected
        """
        if SQL_INJECTION_REGEX.search(v):
            raise ValueError(
                "Invalid characters in search term. "
                "Please use only letters, numbers, spaces, and hyphens."
            )
        return v.strip()

    @field_validator("search_term")
    @classmethod
    def validate_reasonable_characters(cls, v: str) -> str:
        """Ensure search term contains only reasonable characters.

        Args:
            v: Input search term

        Returns:
            Validated search term

        Raises:
            ValueError: If invalid characters found
        """
        # Allow letters, numbers, spaces, hyphens, periods, and apostrophes
        # (e.g., "O'Neal", "J.R. Smith")
        if not re.match(r"^[a-zA-Z0-9\s\-.']+$", v):
            raise ValueError(
                "Search term contains invalid characters. "
                "Please use only letters, numbers, spaces, hyphens, "
                "periods, and apostrophes."
            )
        return v


def validate_search_term(term: str) -> str | None:
    """Validate a player search term.

    Args:
        term: Raw search input

    Returns:
        Validated and cleaned search term, or None if invalid
    """
    try:
        validated = PlayerSearchInput(search_term=term)
        return validated.search_term
    except ValueError:
        return None


def is_valid_search_term(term: str) -> bool:
    """Check if a search term is valid without raising exceptions.

    Args:
        term: Raw search input

    Returns:
        True if valid, False otherwise
    """
    return validate_search_term(term) is not None
