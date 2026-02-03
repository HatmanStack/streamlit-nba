"""Tests for input validation module."""

import pytest

from src.validation.inputs import (
    PlayerSearchInput,
    is_valid_search_term,
    validate_search_term,
)


class TestPlayerSearchInput:
    """Tests for PlayerSearchInput validation."""

    def test_valid_simple_name(self) -> None:
        """Test valid simple name passes validation."""
        result = PlayerSearchInput(search_term="James")
        assert result.search_term == "James"

    def test_valid_full_name(self) -> None:
        """Test valid full name passes validation."""
        result = PlayerSearchInput(search_term="LeBron James")
        assert result.search_term == "LeBron James"

    def test_valid_name_with_apostrophe(self) -> None:
        """Test name with apostrophe passes validation."""
        result = PlayerSearchInput(search_term="Shaquille O'Neal")
        assert result.search_term == "Shaquille O'Neal"

    def test_valid_name_with_period(self) -> None:
        """Test name with period passes validation."""
        result = PlayerSearchInput(search_term="J.R. Smith")
        assert result.search_term == "J.R. Smith"

    def test_valid_name_with_hyphen(self) -> None:
        """Test name with hyphen passes validation."""
        result = PlayerSearchInput(search_term="Kareem Abdul-Jabbar")
        assert result.search_term == "Kareem Abdul-Jabbar"

    def test_strips_whitespace(self) -> None:
        """Test that whitespace is stripped."""
        result = PlayerSearchInput(search_term="  James  ")
        assert result.search_term == "James"


class TestSqlInjectionRejection:
    """Tests for SQL injection pattern rejection."""

    @pytest.mark.parametrize(
        "malicious_input",
        [
            "'; DROP TABLE NBA;--",
            "James'; DELETE FROM NBA--",
            "' OR '1'='1",
            "James' UNION SELECT * FROM passwords--",
            "James; SELECT * FROM users",
            "/*comment*/James",
            "James*/DROP TABLE/*",
            "' OR 1=1--",
            "James' AND 1=1--",
            "Robert'); DROP TABLE Students;--",
        ],
    )
    def test_rejects_sql_injection(self, malicious_input: str) -> None:
        """Test that SQL injection patterns are rejected."""
        with pytest.raises(ValueError) as exc_info:
            PlayerSearchInput(search_term=malicious_input)

        # Should mention invalid characters
        assert "Invalid" in str(exc_info.value) or "invalid" in str(exc_info.value)

    @pytest.mark.parametrize(
        "invalid_input",
        [
            "James<script>",
            "James&nbsp;",
            "James@#$%",
            "James\\nNewline",
            "James\x00null",
        ],
    )
    def test_rejects_special_characters(self, invalid_input: str) -> None:
        """Test that special characters are rejected."""
        with pytest.raises(ValueError):
            PlayerSearchInput(search_term=invalid_input)

    def test_rejects_empty_string(self) -> None:
        """Test that empty string is rejected."""
        with pytest.raises(ValueError):
            PlayerSearchInput(search_term="")

    def test_rejects_too_long(self) -> None:
        """Test that overly long input is rejected."""
        with pytest.raises(ValueError):
            PlayerSearchInput(search_term="A" * 101)


class TestValidateSearchTerm:
    """Tests for validate_search_term helper function."""

    def test_returns_cleaned_term(self) -> None:
        """Test that valid term is returned cleaned."""
        result = validate_search_term("  James  ")
        assert result == "James"

    def test_returns_none_for_invalid(self) -> None:
        """Test that invalid input returns None."""
        result = validate_search_term("'; DROP TABLE--")
        assert result is None

    def test_returns_none_for_empty(self) -> None:
        """Test that empty input returns None."""
        result = validate_search_term("")
        assert result is None


class TestIsValidSearchTerm:
    """Tests for is_valid_search_term helper function."""

    def test_returns_true_for_valid(self) -> None:
        """Test returns True for valid input."""
        assert is_valid_search_term("James") is True
        assert is_valid_search_term("LeBron James") is True
        assert is_valid_search_term("O'Neal") is True

    def test_returns_false_for_invalid(self) -> None:
        """Test returns False for invalid input."""
        assert is_valid_search_term("'; DROP--") is False
        assert is_valid_search_term("") is False
        assert is_valid_search_term("<script>") is False
