"""The script for running the streamlit app"""

import streamlit as st

from cookie_tools import CookieTools
from ui_components import UiComponents

st.set_page_config(page_title="Day Tracker", page_icon="🗓️", layout="centered")
CookieTools.setup_cookies()
if CookieTools.verify_password_cookie():
    UiComponents.logged_in_display()
else:
    UiComponents.logged_out_display()
