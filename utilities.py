"""Module for most things log related"""

from datetime import datetime
from typing import Union, Tuple

import math
import pandas as pd
import toml

from filenames import constant_file, log_file, planned_file


class Logs:
    """Class containing log related methods"""

    DATE = None

    @classmethod
    def check_constant(cls) -> bool:
        """Checks whether the constant file exists"""

        try:
            _ = toml.load(constant_file())
            return True
        except FileNotFoundError:
            return False

    @classmethod
    def _create_day_dataframe(cls, day: str, date: str) -> pd.DataFrame:
        """Method for a creating day's dataframe"""

        def tasks_to_dict(tasks: list, prefix) -> dict:
            """Places a task list into a suitable dictionary"""
            return {
                f"{prefix}-{task_name}": ["None"]
                for task_name in tasks}

        def planned_dict() -> dict:
            """Create a dictionary from planned actions,
            then wipes planned actions"""

            try:
                planned = toml.load(planned_file())
            except FileNotFoundError:
                planned = {"tasks": []}
            with open(file=planned_file(), mode="w",
                      encoding="utf-8") as plan_file:
                toml.dump({"tasks": []}, plan_file)
            return tasks_to_dict(tasks=planned["tasks"], prefix="planned")

        actions = toml.load(constant_file())

        day_dataframe = pd.DataFrame(data={
            "date": [date],
            **tasks_to_dict(tasks=actions["morning"], prefix="morning"),
            **tasks_to_dict(tasks=actions["evening"], prefix="evening"),
            **tasks_to_dict(tasks=actions[day]["general"], prefix="general"),
            **tasks_to_dict(tasks=actions[day]["food"], prefix="food"),
            **planned_dict(),
        })

        return day_dataframe.set_index("date", drop=True)

    @classmethod
    def _log_setup(cls) -> pd.DataFrame:
        """Method for creating/getting the log file"""

        try:
            return pd.read_csv(filepath_or_buffer=log_file(),
                               index_col="date")
        except FileNotFoundError:
            day = datetime.now().strftime("%A")
            date = datetime.now().strftime("%d/%m/%Y")
            cls._create_day_dataframe(day=day, date=date
                                      ).to_csv(path_or_buf=log_file())
            return cls._create_day_dataframe(day=day, date=date)

    @classmethod
    def _update_log_file(cls, date: str,
                         existing_dataframe: pd.DataFrame) -> None:
        """Method for updating the log file"""
        dates = [(date.strftime("%A"), date.strftime("%d/%m/%Y")) for date in
                 pd.date_range(
                     start=cls._get_max_date(dataframe=existing_dataframe),
                     end=date
                 )][1:]

        day_dataframes = [cls._create_day_dataframe(day=date[0], date=date[1]
                                                    ) for date in dates]

        new_dataframe = pd.concat([existing_dataframe, *day_dataframes],
                                  join="outer")
        new_dataframe.to_csv(path_or_buf=log_file())

    @classmethod
    def _get_min_date(cls, dataframe: pd.DataFrame) -> str:
        """Method for getting the earliest date of the log file"""
        return dataframe.index[0]

    @classmethod
    def _get_max_date(cls, dataframe: pd.DataFrame) -> str:
        """Method for getting the latest date of the log file"""
        return dataframe.index[-1]

    @classmethod
    def config(cls, date: str, ) -> str:
        """Method for setting up the log file"""

        log_dataframe = cls._log_setup()
        if cls._get_max_date(dataframe=log_dataframe) != date:
            cls._update_log_file(date=date,
                                 existing_dataframe=log_dataframe)
        return cls._get_min_date(dataframe=log_dataframe)

    @classmethod
    def set_date(cls, date: str) -> None:
        """Method for setting the date to use"""
        cls.DATE = date

    @classmethod
    def _get_values(cls, dataframe: pd.DataFrame, date: str) -> list:
        """Method for returning a list of all task values from a given date"""
        return [item for item in list(dataframe.loc[date]) if not pd.isnull(item)]

    @classmethod
    def _get_score(cls, values: list) -> int:
        """Method for getting the score from a list of values"""
        return sum(int(item) for item in values if item != "None")

    @classmethod
    def _get_start_progress(cls, dataframe: pd.DataFrame) -> Tuple[float, float]:
        """Method for getting the current progress value from the log file"""

        multipliers = []
        for date_index in dataframe.index:
            if date_index == cls.DATE:
                break
            values = cls._get_values(dataframe=dataframe, date=date_index)
            multipliers.append(
                1 + (0.01 * (cls._get_score(values=values) / len(values))))

        if not multipliers:
            return 1, 0

        delta = multipliers[-1] - 1
        progress = math.prod(multipliers)
        return progress, delta

    @classmethod
    def _get_new_progress(cls, dataframe: pd.DataFrame,
                          start_value: float) -> Tuple[float, float]:
        """Method for getting the new progress
        value from the current progress and score"""

        values = cls._get_values(dataframe=dataframe, date=cls.DATE)
        new_delta = (0.01 * (cls._get_score(values=values) / len(values)))
        multiplier = 1 + new_delta
        new_value = start_value * multiplier
        return new_value, new_delta

    @classmethod
    def basic_info(cls) -> dict:
        """Method for returning basic info from the log file"""

        dataframe = pd.read_csv(filepath_or_buffer=log_file(),
                                index_col="date")
        values = cls._get_values(dataframe=dataframe, date=cls.DATE)
        start_progress = cls._get_start_progress(dataframe=dataframe)
        return {
            "score": cls._get_score(values),
            "total_score": len(values),
            "start_progress": start_progress,
            "new_progress": cls._get_new_progress(dataframe=dataframe,
                                                  start_value=start_progress[0])
        }

    @classmethod
    def get_actions(cls) -> dict:
        """Method for returning available tasks from the log file"""

        dataframe = pd.read_csv(filepath_or_buffer=log_file(),
                                index_col="date")
        actions = list(dataframe.loc[cls.DATE].dropna().index)
        action_dict = {
            "morning": [action.removeprefix("morning-") for action in actions if
                        action.startswith("morning")],
            "evening": [action.removeprefix("evening-") for action in actions if
                        action.startswith("evening")],
            "general": [action.removeprefix("general-") for action in actions if
                        action.startswith("general")],
            "food": [action.removeprefix("food-") for action in actions if
                     action.startswith("food")],
            "planned": [action.removeprefix("planned-") for action in actions if
                        action.startswith("planned")],
        }
        return action_dict

    @classmethod
    def get_action_value(cls, section: str, name: str) -> Union[int, str]:
        """Method for getting a task value from the log file"""

        dataframe = pd.read_csv(filepath_or_buffer=log_file(),
                                index_col="date")
        return dataframe.loc[cls.DATE][f"{section}-{name}"]

    @classmethod
    def set_action_value(cls, section: str, name: str,
                         value: Union[str, int]) -> None:
        """Method for setting a task value in the log file"""

        dataframe = pd.read_csv(filepath_or_buffer=log_file(),
                                index_col="date")
        dataframe.at[cls.DATE, f"{section}-{name}"] = value
        dataframe.to_csv(path_or_buf=log_file())

    @classmethod
    def get_planned_values(cls) -> list:
        """Method for getting the planned tasks from the plan file"""

        try:
            return toml.load(planned_file())["tasks"]
        except FileNotFoundError:
            with open(file=planned_file(), mode="w", encoding="utf-8") as file:
                toml.dump({"tasks": []}, file)
            return []

    @classmethod
    def set_planned_values(cls, task_list: list) -> None:
        """Method for setting the planned tasks in plan file"""

        toml_data = toml.load(planned_file())
        toml_data["tasks"] = task_list
        with open(file=planned_file(), mode="w", encoding="utf-8") as file:
            toml.dump(toml_data, file)
