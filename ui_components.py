"""Module for most things UI related"""

from datetime import datetime, timedelta
import time

import numpy as np
import streamlit as st
import toml

from toml_tools import TomlTools
from objectives import BasicObjective, WriteObjective, PlanObjective


class UiComponents:
    """Class containing useful UI functions"""

    @classmethod
    def _value_display(cls):
        """Method for displaying the UI for the value"""

        def value_as_string():
            """Function for returning a value as a string"""

            if value > 10:
                return f"{round(value, 2)}x"

            else:
                return f"{round(value * 100, 2)}%"

        def delta_as_string():
            """Function for returning a value as a string"""

            return f"{round(delta * 100, 2)}%"

        toml_data = TomlTools.get_progress()
        value = toml_data.get("progress", 0)
        delta = toml_data.get("delta", 0)
        st.metric(label="Value",
                  value=value_as_string(),
                  delta=delta_as_string())

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
        total_score = len(TomlTools._get_flat_current_values())
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
    @st.experimental_memo
    def _get_data(cls, file_date: str):
        """Method for getting the data from current.toml"""

        file_date.title()  # used for separating caching
        with open(file="current.toml", mode="r", encoding="utf-8") as file:
            return file.read()

    @classmethod
    def _finish_day_display(cls, date: str):
        """Method for displaying the UI after a day has finished"""

        def downloading():
            st.session_state["downloading"] = True

        filename_date = date.replace("/", ",")

        st.download_button(label="Download Log",
                           data=cls._get_data(filename_date),
                           file_name=f"log_{filename_date}.toml",
                           mime="application/toml",
                           key="downloader", on_click=downloading, )

        if st.session_state.get("downloading", False):
            with st.spinner(text="Generating log"):
                time.sleep(1)
            st.session_state["downloading"] = False
            st.session_state["downloaded"] = True
            st.experimental_rerun()

    @classmethod
    def _same_day_display(cls, day: str, date: str):
        """Method for displaying the UI if the day
        is the same as the previous run"""

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

    @classmethod
    def _different_day_display(cls, current_day: str, current_date: str):
        """Method for displaying the UI if the day
        is different to the previous run"""

        file_date = TomlTools.get_date()

        if file_date is None:
            TomlTools.create_current(day=current_day, date=current_date)
            st.experimental_rerun()
            return  # unneeded expect for IDE warning

        if st.session_state.get("downloaded", False):
            st.session_state["downloaded"] = False
            TomlTools.set_progress()
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
            return

        TomlTools.set_all_action_values(value=-1)
        st.title(f"Log date: {file_date}")
        st.title(f"Current date: {current_date}")
        cls._finish_day_display(date=file_date)

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
