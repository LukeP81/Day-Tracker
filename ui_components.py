"""Module for most things UI related"""

from datetime import datetime, timedelta

import numpy as np
import streamlit as st
import toml

from toml_tools import TomlTools
from objectives import BasicObjective, WriteObjective, PlanObjective


# pylint: disable=too-few-public-methods
class UiComponents:
    """Class containing useful UI functions"""

    @classmethod
    def _value_display(cls):
        """Method for displaying the UI for the value"""

        def value_as_string(val):
            """Function for returning a value as a string"""

            return f"{round(val, 2)}x" if val > 10 else f"{round(val * 100, 2)}%"

        def delta_as_string(val):
            """Function for returning a value as a string"""

            return f"{round(val * 100, 2)}%"

        current_value, current_delta = TomlTools.get_current_progress()
        new_value, new_delta = TomlTools.get_new_progress()

        current_col, new_col = st.columns(2)
        with current_col:
            st.metric(label="Start Value",
                      value=value_as_string(current_value),
                      delta=delta_as_string(current_delta))
        with new_col:
            st.metric(label="Current Value",
                      value=value_as_string(new_value),
                      delta=delta_as_string(new_delta))

    @classmethod
    def _color_config(cls, current_score: int, total_score: int):
        """Method for setting the primary color of the theme"""

        # sort colours
        blue = 0
        if current_score > 0:
            green = 255
            red = int(np.ceil((1 - (current_score / total_score)) * 255))
        elif current_score < 0:
            green = int(np.ceil((1 - (-current_score / total_score)) * 255))
            red = 255
        else:
            green = 255
            red = 255
        colour_tuple = (red, green, blue)
        colour = '#' + ''.join(f'{i:02X}' for i in colour_tuple)

        current_settings = toml.load(".streamlit/config.toml")
        if current_settings["theme"]["primaryColor"] != colour:
            current_settings["theme"]["primaryColor"] = colour
            with open(file=".streamlit/config.toml", mode="w",
                      encoding="utf-8") as file:
                toml.dump(current_settings, file)
            st.experimental_rerun()

    @classmethod
    def _score_display(cls):
        """Method for displaying the UI for the score"""

        current_score = TomlTools.get_score()
        total_score = TomlTools.get_total_score()
        st.slider(label="Score",
                  min_value=-total_score, max_value=total_score,
                  value=current_score)
        cls._color_config(current_score=current_score, total_score=total_score)

    @classmethod
    def _create_objective_forms(cls, section: str):
        """Method for displaying the UI for the task forms"""

        special = toml.load("constant.toml")["Special"]
        actions = toml.load("current.toml")[section]
        for action in list(actions.keys()):
            objective_types = {
                "basic": BasicObjective,
                "plan": PlanObjective,
                "write": WriteObjective
            }
            kwargs = {"section": section, "name": action}

            if special.get(action, ["", ])[0] == "p":
                objective_type = "plan"

            elif special.get(action, ["", ])[0] == "w":
                objective_type = "write"
                kwargs["to_write"] = special[action][1]

            else:
                objective_type = "basic"

            objective = objective_types[objective_type](**kwargs)
            objective.display()

    @classmethod
    def _check_log_exists(cls) -> bool:
        """Method for checking that the log file exists"""

        try:
            with open(file="log.csv", mode="r", encoding="utf-8"):
                return True
        except FileNotFoundError:
            return False

    @classmethod
    @st.experimental_memo
    def _get_data(cls, current_date: str):
        """Method for getting the data from current.toml"""

        _ = current_date  # used for separating caching
        with open(file="log.csv", mode="r", encoding="utf-8") as file:
            return file.read()

    @classmethod
    def _same_day_display(cls, day: str, date: str):
        """Method for displaying the UI if the day is
        the same as the previous run"""

        st.title(f"{day} {date}")
        cls._value_display()
        cls._score_display()

        with st.expander(label="Morning"):
            cls._create_objective_forms("morning")

        with st.expander(label="Specific"):
            general_tab, food_tab, planned_tab = st.tabs(
                ["General", "Food", "Planned"])
            with general_tab:
                cls._create_objective_forms("general")
            with food_tab:
                cls._create_objective_forms("food")
            with planned_tab:
                cls._create_objective_forms("planned")

        with st.expander(label="Evening"):
            cls._create_objective_forms("evening")

        if cls._check_log_exists():
            st.download_button(label="Download Log",
                               data=cls._get_data(date),
                               file_name="day_tracker_log.csv",
                               mime="text/csv",
                               key="downloader")

    @classmethod
    def _different_day_display(cls, current_day: str, current_date: str):
        """Method for displaying the UI if the day
        is different to the previous run"""

        file_date = TomlTools.get_date()

        if file_date is None:
            TomlTools.create_current(day=current_day, date=current_date)
            st.experimental_rerun()

        st.title("Processing Log")
        TomlTools.set_all_action_values(value=-1)
        TomlTools.set_progress()
        TomlTools.set_log_file()
        file_datetime = datetime.strptime(
            file_date, "%d/%m/%Y"
        ) + timedelta(
            days=1,
            hours=12  # avoid bst errors
        )
        new_date = (file_datetime.strftime("%d/%m/%Y"))
        new_day = file_datetime.strftime("%A")
        TomlTools.create_current(day=new_day, date=new_date)
        st.experimental_rerun()

    @classmethod
    def display(cls):
        """Method for displaying the UI if the user is logged in"""

        day = (datetime.now().strftime("%A"))
        date = (datetime.now().strftime("%d/%m/%Y"))
        same_day = TomlTools.check_date(date=date)
        if same_day:
            cls._same_day_display(day=day, date=date)
        else:
            cls._different_day_display(current_day=day, current_date=date)
