"""The script for running the streamlit app"""

import streamlit as st

from filenames import log_file
from ui_components import UiComponents

st.set_page_config(page_title="Day Tracker", page_icon="🗓️", layout="centered")

if st.experimental_user["email"] is None:
    st.header("Please log in to streamlit to continue")
    st.stop()

try:
    UiComponents.display()

# unsure of error, need to always have log
except Exception as e:  # pylint:disable=broad-except
    st.write(e)
    with open(file=log_file(), mode="r", encoding="utf-8") as file:
        st.download_button(label="Download Log",
                           data=file.read(),
                           file_name="day_tracker_log.csv",
                           mime="text/csv",
                           key="downloader")
