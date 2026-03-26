"""HTML sanitization utilities for XSS protection."""

import html
from typing import Literal

import streamlit as st

# Valid heading levels
HeadingLevel = Literal[1, 2, 3, 4, 5, 6]


def escape_html(text: str) -> str:
    """Escape HTML special characters to prevent XSS.

    Args:
        text: Raw text that may contain HTML

    Returns:
        Escaped text safe for HTML insertion
    """
    return html.escape(str(text))


def safe_heading(
    text: str,
    level: HeadingLevel = 1,
    color: str = "steelblue",
    align: str = "center",
) -> None:
    """Render a heading with escaped text to prevent XSS.

    Args:
        text: Heading text (will be escaped)
        level: Heading level 1-6
        color: CSS color value
        align: CSS text-align value
    """
    # Escape all user-provided values
    safe_text = escape_html(text)
    safe_color = escape_html(color)
    safe_align = escape_html(align)

    st.markdown(
        f"<h{level} style='text-align: {safe_align}; color: {safe_color};'>"
        f"{safe_text}</h{level}>",
        unsafe_allow_html=True,
    )


def safe_paragraph(
    text: str,
    color: str = "white",
    align: str = "center",
) -> None:
    """Render a paragraph with escaped text to prevent XSS.

    Args:
        text: Paragraph text (will be escaped)
        color: CSS color value
        align: CSS text-align value
    """
    safe_text = escape_html(text)
    safe_color = escape_html(color)
    safe_align = escape_html(align)

    st.markdown(
        f"<p style='text-align: {safe_align}; color: {safe_color};'>{safe_text}</p>",
        unsafe_allow_html=True,
    )
