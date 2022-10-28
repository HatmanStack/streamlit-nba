import streamlit as st
import pandas as pd
import snowflake.connector

def on_page_load():
    st.set_page_config(layout="wide")
on_page_load()

st.markdown("<h1 style='text-align: center; color: steelblue;'>NBA</h1>", unsafe_allow_html=True)

st.markdown("<h5 style='text-align: center; color: white;'>A Simple app to test your skill in building a Team based on career stats to compete with a Computer</h5>", unsafe_allow_html=True)


