"""NBA Team Builder Application - Entry Point."""

import streamlit as st

from src.utils.html import safe_heading, safe_paragraph


def on_page_load() -> None:
    """Configure page settings."""
    st.set_page_config(layout="wide")


on_page_load()

safe_heading("NBA", level=1, color="steelblue")

safe_paragraph(
    "A Simple app to test your skill in building a Team based on "
    "career stats to compete with a Computer",
    color="white",
)


