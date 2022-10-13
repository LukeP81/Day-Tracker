"""The script for running the streamlit app"""

import streamlit as st

from ui_components import UiComponents

st.set_page_config(page_title="Day Tracker", page_icon="🗓️", layout="centered")
try:
    UiComponents.display()

# unsure of error, need to always have log
except BaseException as e:  # pylint:disable=broad-except
    st.write(e)
    with open(file="log.csv", mode="r", encoding="utf-8") as file:
        st.download_button(label="Download Log",
                           data=file.read(),
                           file_name="day_tracker_log.csv",
                           mime="text/csv",
                           key="downloader")
