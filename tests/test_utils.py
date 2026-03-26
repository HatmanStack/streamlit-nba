"""Tests for HTML utility functions."""

from unittest.mock import patch

from src.utils.html import escape_html


class TestEscapeHtml:
    """Tests for escape_html function."""

    def test_escapes_angle_brackets(self) -> None:
        """Verify < and > are escaped."""
        assert "&lt;" in escape_html("<div>")
        assert "&gt;" in escape_html("<div>")

    def test_escapes_ampersand(self) -> None:
        """Verify & is escaped."""
        assert "&amp;" in escape_html("a & b")

    def test_escapes_double_quotes(self) -> None:
        """Verify double quotes are escaped."""
        assert "&quot;" in escape_html('say "hello"')

    def test_escapes_single_quotes(self) -> None:
        """Verify single quotes are escaped."""
        assert "&#x27;" in escape_html("it's")

    def test_safe_strings_unchanged(self) -> None:
        """Verify safe strings pass through unmodified."""
        assert escape_html("Hello World") == "Hello World"
        assert escape_html("abc123") == "abc123"
        assert escape_html("") == ""


class TestSafeHeading:
    """Tests for safe_heading function."""

    def test_escapes_xss_payload(self) -> None:
        """Verify XSS payloads are escaped in heading output."""
        with patch("src.utils.html.st") as mock_st:
            from src.utils.html import safe_heading

            safe_heading("<script>alert(1)</script>")

            call_args = mock_st.markdown.call_args
            rendered_html = call_args[0][0]
            assert "<script>" not in rendered_html
            assert "&lt;script&gt;" in rendered_html

    def test_renders_correct_heading_level(self) -> None:
        """Verify heading level is used in output."""
        with patch("src.utils.html.st") as mock_st:
            from src.utils.html import safe_heading

            safe_heading("Title", level=3)

            rendered_html = mock_st.markdown.call_args[0][0]
            assert "<h3" in rendered_html
            assert "</h3>" in rendered_html

    def test_uses_unsafe_allow_html(self) -> None:
        """Verify markdown is called with unsafe_allow_html=True."""
        with patch("src.utils.html.st") as mock_st:
            from src.utils.html import safe_heading

            safe_heading("Title")

            mock_st.markdown.assert_called_once()
            assert mock_st.markdown.call_args[1]["unsafe_allow_html"] is True


class TestSafeParagraph:
    """Tests for safe_paragraph function."""

    def test_escapes_xss_payload(self) -> None:
        """Verify XSS payloads are escaped in paragraph output."""
        with patch("src.utils.html.st") as mock_st:
            from src.utils.html import safe_paragraph

            safe_paragraph("<img onerror=alert(1) src=x>")

            rendered_html = mock_st.markdown.call_args[0][0]
            assert "<img" not in rendered_html
            assert "&lt;img" in rendered_html

    def test_renders_paragraph_tag(self) -> None:
        """Verify paragraph tag is used in output."""
        with patch("src.utils.html.st") as mock_st:
            from src.utils.html import safe_paragraph

            safe_paragraph("Hello")

            rendered_html = mock_st.markdown.call_args[0][0]
            assert "<p " in rendered_html
            assert "</p>" in rendered_html
            assert "Hello" in rendered_html

    def test_uses_unsafe_allow_html(self) -> None:
        """Verify markdown is called with unsafe_allow_html=True."""
        with patch("src.utils.html.st") as mock_st:
            from src.utils.html import safe_paragraph

            safe_paragraph("Text")

            mock_st.markdown.assert_called_once()
            assert mock_st.markdown.call_args[1]["unsafe_allow_html"] is True
