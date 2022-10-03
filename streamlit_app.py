"""The script for running the streamlit app"""

import streamlit as st

from ui_components import UiComponents

st.set_page_config(page_title="Day Tracker", page_icon="🗓️", layout="centered")
UiComponents.display()
