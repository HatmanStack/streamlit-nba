"""Input validation for user-provided data."""

import re

from pydantic import BaseModel, Field, field_validator


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
    def validate_reasonable_characters(cls, v: str) -> str:
        """Ensure search term contains only reasonable characters.

        Args:
            v: Input search term

        Returns:
            Validated and stripped search term

        Raises:
            ValueError: If invalid characters found
        """
        v = v.strip()
        if not v:
            raise ValueError("Search term cannot be empty.")
        # Allow letters, numbers, spaces, hyphens, periods, and apostrophes
        # (e.g., "O'Neal", "J.R. Smith")
        if not re.match(r"^[a-zA-Z0-9 \-.']+$", v):
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
