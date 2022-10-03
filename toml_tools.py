"""Module for most things toml related"""

from typing import List, Optional, Union

import toml


class TomlTools:
    """Class containing useful toml functions"""

    @classmethod
    def get_date(cls) -> Optional[str]:
        """Method for getting the date of current.toml"""

        return toml.load("current.toml").get("date", None)

    @classmethod
    def check_date(cls, date: str) -> bool:
        """Method for checking if the date of current.toml matches"""

        # check if day is the same
        if cls.get_date() == date:
            return True
        return False

    @classmethod
    def create_current(cls, day: str, date: str) -> None:
        """Method for creating a new version of current.toml"""

        def list_to_dict(action_list: List[str]) -> dict:
            """Function for creating a suitable dictionary out of a list"""

            returning_dict = {}
            for action in action_list:
                key = action.replace(" ", "_")
                returning_dict[key] = "None"  # Toml won't work with None
            return returning_dict

        # create dicts from constant actions
        actions = toml.load("constant.toml")
        morning_dict = list_to_dict(action_list=actions["morning"])
        evening_dict = list_to_dict(action_list=actions["evening"])
        general_dict = list_to_dict(action_list=actions[day]["general"])
        food_dict = list_to_dict(action_list=actions[day]["food"])

        # create dicts from planned actions, then wipe planned actions
        actions = toml.load("planned.toml")
        planned_dict = list_to_dict(action_list=actions["tasks"])
        with open(file="planned.toml", mode="w", encoding="utf-8") as file:
            toml.dump({"tasks": []}, file)

        # place dicts into toml file
        current_dict = {
            "date": date,
            "tomorrow": [],
            "morning": morning_dict,
            "evening": evening_dict,
            "general": general_dict,
            "food": food_dict,
            "planned": planned_dict,
        }
        with open(file="current.toml", mode="w", encoding="utf-8") as file:
            toml.dump(current_dict, file)

    @classmethod
    def _get_flat_current_values(cls) -> list:
        """Method for returning a flat list of all current.toml tasks"""

        def extract_nested_values(it):  # pylint:disable=invalid-name
            # https://stackoverflow.com/questions/46845464/cleaner-way-to-unpack-nested-dictionaries
            if isinstance(it, list):
                for sub_it in it:
                    yield from extract_nested_values(sub_it)
            elif isinstance(it, dict):
                for value in it.values():
                    yield from extract_nested_values(value)
            else:
                yield it

        dicts = toml.load("current.toml")
        _ = dicts.pop("date", None)
        _ = dicts.pop("tomorrow", None)
        return list(extract_nested_values(dicts))

    @classmethod
    def get_score(cls) -> int:
        """Method for getting the score from current.toml"""

        score = 0
        values = cls._get_flat_current_values()
        for value in values:
            if value != "None":
                score += int(value)
        return score

    @classmethod
    def get_total_score(cls) -> int:
        """Method for getting the total score"""

        return len(cls._get_flat_current_values())

    @classmethod
    def get_action_value(cls, section: str, name: str) -> Union[int, str]:
        """Method for getting a task value from current.toml"""

        dicts = toml.load("current.toml")
        return dicts[section][name]

    @classmethod
    def set_action_value(cls, section: str, name: str, value: Union[str, int]):
        """Method for setting a task value in current.toml"""

        dicts = toml.load("current.toml")
        dicts[section][name] = value
        with open(file="current.toml", mode="w", encoding="utf-8") as file:
            toml.dump(dicts, file)

    @classmethod
    def set_all_action_values(cls, value: int):
        """Method for setting all the task values in current.toml"""

        toml_data = toml.load("current.toml")
        for section in list(toml_data.keys()):
            if isinstance(toml_data[section], dict):
                for action in list(toml_data[section].keys()):
                    if toml_data[section][action] == "None":
                        toml_data[section][action] = value

        with open(file="current.toml", mode="w", encoding="utf-8") as file:
            toml.dump(toml_data, file)

    @classmethod
    def get_planned_values(cls) -> list:
        """Method for getting the planned tasks from planned.toml"""

        return toml.load("planned.toml")["tasks"]

    @classmethod
    def set_planned_values(cls, task_list: list):
        """Method for setting the planned tasks in planned.toml"""

        toml_data = toml.load("planned.toml")
        toml_data["tasks"] = task_list
        with open(file="planned.toml", mode="w", encoding="utf-8") as file:
            toml.dump(toml_data, file)

    @classmethod
    def get_progress(cls) -> dict:
        """Method for getting the progress value from progress.toml"""

        return toml.load("progress.toml")

    @classmethod
    def set_progress(cls):
        """Method for setting the progress value in progress.toml"""

        score = cls.get_score()
        total_score = len(cls._get_flat_current_values())
        percent_change = (0.01 * (score / total_score))
        multiplier = 1 + percent_change
        toml_data = toml.load("progress.toml")
        toml_data["progress"] *= multiplier
        toml_data["delta"] = percent_change
        with open(file="progress.toml", mode="w", encoding="utf-8") as file:
            toml.dump(toml_data, file)
