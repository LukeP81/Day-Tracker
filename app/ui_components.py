from datetime import datetime, timedelta

import numpy as np
import streamlit as st
import toml
import time

from app.toml_tools import TomlTools
from app.objectives import BasicObjective, WriteObjective, PlanObjective
from app.cookie_tools import CookieTools


class UiComponents:

    @classmethod
    def color_config(cls, current_score: int, total_score: int):
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
            with open(".streamlit/config.toml", "w") as file:
                toml.dump(current_settings, file)
            st.experimental_rerun()

    @classmethod
    def score_display(cls):
        current_score = TomlTools.get_score()
        total_score = len(TomlTools.get_flat_current_values())
        st.slider(label="Score",
                  min_value=-total_score, max_value=total_score,
                  value=current_score)
        cls.color_config(current_score=current_score, total_score=total_score)

    @classmethod
    def create_objective_forms(cls, section: str):
        special = toml.load("app/constant.toml")["Special"]
        actions = toml.load("app/current.toml")[section]
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
    def get_data(cls, file_date: str):
        file_date.title()  # used for separating caching
        with open("app/current.toml", "r") as file:
            return file.read()

    @classmethod
    def finish_day_display(cls, date: str):
        def downloading():
            st.session_state["downloading"] = True

        filename_date = date.replace("/", ",")

        st.download_button(label="Download Log", data=cls.get_data(filename_date),
                           file_name=f"log_{filename_date}.toml", mime="application/toml",
                           key="downloader", on_click=downloading, )
        if st.session_state.get("downloading", False):
            with st.spinner(text="Generating log"):
                time.sleep(1)
            st.session_state["downloading"] = False
            st.session_state["downloaded"] = True
            st.experimental_rerun()

    @classmethod
    def same_day_display(cls, day: str, date: str):
        st.title(f"{day} {date}")
        st.subheader(f"Value: {TomlTools.get_progress()}")
        cls.score_display()
        with st.expander(label="Morning"):
            cls.create_objective_forms("morning")
        with st.expander(label="Specific"):
            general_tab, food_tab, planned_tab = st.tabs(["General", "Food", "Planned"])
            with general_tab:
                cls.create_objective_forms("general")
            with food_tab:
                cls.create_objective_forms("food")
            with planned_tab:
                cls.create_objective_forms("planned")
        with st.expander(label="Evening"):
            cls.create_objective_forms("evening")

    @classmethod
    def different_day_display(cls, current_day: str, current_date: str):
        file_date = TomlTools.get_date()

        if file_date is None:
            TomlTools.create_current(day=current_day, date=current_date)
            st.experimental_rerun()
            return  # unneeded expect for IDE warning

        if st.session_state.get("downloaded", False):
            st.session_state["downloaded"] = False
            TomlTools.set_progress()
            file_datetime = datetime.strptime(file_date, "%d/%m/%Y") + timedelta(days=1, hours=12)  # avoid bst errors
            new_date = (file_datetime.strftime("%d/%m/%Y"))
            new_day = file_datetime.strftime("%A")
            TomlTools.create_current(day=new_day, date=new_date)
            st.experimental_rerun()
            return

        TomlTools.set_all_action_values(value=-1)
        st.title(f"Log date: {file_date}")
        st.title(f"Current date: {current_date}")
        cls.finish_day_display(date=file_date)

    @classmethod
    def logged_in_display(cls):
        day = (datetime.now().strftime("%A"))
        date = (datetime.now().strftime("%d/%m/%Y"))
        same_day = TomlTools.check_date(date=date)
        if same_day:
            cls.same_day_display(day=day, date=date)
        else:
            cls.different_day_display(current_day=day, current_date=date)

    @classmethod
    def logged_out_display(cls):
        with st.form(key="Login details"):
            password = st.text_input(label="Password", type="password",
                                     placeholder="Enter password here")
            submit = st.form_submit_button()
            if submit:
                CookieTools.set_password_cookie(password=password)
