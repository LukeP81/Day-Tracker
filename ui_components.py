"""Module for most things UI related"""

from datetime import datetime
from typing import Tuple
import numpy as np
import streamlit as st
import toml

from utilities import Logs
from objectives import BasicObjective, WriteObjective, PlanObjective


# pylint: disable=too-few-public-methods
class UiComponents:
    """Class containing useful UI functions"""

    @classmethod
    def _value_display(cls, current_progress: Tuple[float, float],
                       new_progress: Tuple[float, float]) -> None:
        """Method for displaying the UI for the value"""

        def value_as_string(val: float) -> str:
            """Function for returning a value as a string"""
            return f"{round(val, 2)}x" if val > 10 else f"{round(val * 100, 2)}%"

        def delta_as_string(val: float) -> str:
            """Function for returning a value as a string"""
            return f"{round(val * 100, 2)}%"

        current_value, current_delta = current_progress
        new_value, new_delta = new_progress

        current_col, new_col = st.columns(2)
        with current_col:
            st.metric(label="Start Value",
                      value=value_as_string(current_value),
                      delta=delta_as_string(current_delta))
        with new_col:
            st.metric(label="EOD Value",
                      value=value_as_string(new_value),
                      delta=delta_as_string(new_delta))

    @classmethod
    def _color_config(cls, current_score: int, total_score: int) -> None:
        """Method for setting the primary color of the theme"""

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

        colour = '#' + ''.join(f'{i:02X}' for i in (red, green, blue))

        current_settings = toml.load(".streamlit/config.toml")
        if current_settings["theme"]["primaryColor"] != colour:
            current_settings["theme"]["primaryColor"] = colour
            with open(file=".streamlit/config.toml", mode="w",
                      encoding="utf-8") as file:
                toml.dump(current_settings, file)
            st.experimental_rerun()

    @classmethod
    def _score_display(cls, score: int, total_score: int) -> None:
        """Method for displaying the UI for the score"""

        st.slider(label="Score",
                  min_value=-total_score, max_value=total_score,
                  value=score)
        cls._color_config(current_score=score, total_score=total_score)

    @classmethod
    def _create_objective_forms(cls, tasks: dict, section: str) -> None:
        """Method for displaying the UI for the task forms"""

        special = toml.load("constant.toml")["Special"]
        actions = tasks[section]
        for action in actions:
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
    def _get_data(cls) -> str:
        """Method for getting the data from log.csv"""

        with open(file="log.csv", mode="r", encoding="utf-8") as file:
            return file.read()

    @classmethod
    def _show_objectives(cls, day: str, date: str) -> None:
        """Method for displaying the UI if the day is
        the same as the previous run"""

        st.title(f"{day} {date}")
        info = Logs.basic_info()
        cls._value_display(current_progress=info["start_progress"],
                           new_progress=info["new_progress"])
        cls._score_display(score=info["score"], total_score=info["total_score"])

        tasks = Logs.get_actions()

        with st.expander(label="Morning"):
            cls._create_objective_forms(tasks=tasks, section="morning", )
        with st.expander(label="Specific"):
            general_tab, food_tab, planned_tab = st.tabs(
                ["General", "Food", "Planned"])
            with general_tab:
                cls._create_objective_forms(tasks=tasks, section="general", )
            with food_tab:
                cls._create_objective_forms(tasks=tasks, section="food", )
            with planned_tab:
                cls._create_objective_forms(tasks=tasks, section="planned", )
        with st.expander(label="Evening"):
            cls._create_objective_forms(tasks=tasks, section="evening", )

        st.download_button(label="Download Log",
                           data=cls._get_data(),
                           file_name="day_tracker_log.csv",
                           mime="text/csv",
                           key="downloader")

    @classmethod
    def display(cls) -> None:
        """Method for displaying the UI"""

        current_time = datetime.now()
        current_day = current_time.strftime("%A")
        current_date = current_time.strftime("%d/%m/%Y")

        min_date = Logs.config(day=current_day, date=current_date)
        min_value = datetime.date(
            datetime.strptime(min_date, "%d/%m/%Y"))
        selected = st.sidebar.date_input(label="Select Day", value=current_time,
                                         min_value=min_value,
                                         max_value=current_time)
        selected_day = (selected.strftime("%A"))
        selected_date = (selected.strftime("%d/%m/%Y"))
        Logs.set_date(selected_date)

        cls._show_objectives(day=selected_day, date=selected_date)
