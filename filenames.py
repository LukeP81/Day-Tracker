"""Module for filenames"""

import streamlit as st


def constant_file() -> str:
    """Returns the filename for the constant file matching the user"""
    return st.experimental_user["email"] + "_constant.toml"


def log_file() -> str:
    """Returns the filename for the log file matching the user"""
    return st.experimental_user["email"] + "_log.csv"


def planned_file() -> str:
    """Returns the filename for the planned file matching the user"""
    return st.experimental_user["email"] + "_planned.toml"
