"""NBA Team Builder Application - Entry Point."""

from src.config import configure_page
from src.utils.html import safe_heading, safe_paragraph

configure_page()

safe_heading("NBA", level=1, color="steelblue")

safe_paragraph(
    "A Simple app to test your skill in building a Team based on "
    "career stats to compete with a Computer",
    color="white",
)


