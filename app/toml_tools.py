from typing import List, Optional, Union

import toml


class TomlTools:

    @classmethod
    def get_date(cls) -> Optional[str]:
        return toml.load("app/current.toml").get("date", None)

    @classmethod
    def check_date(cls, date: str) -> bool:
        # check if day is the same
        if cls.get_date() == date:
            return True
        return False

    @classmethod
    def create_current(cls, day: str, date: str) -> None:
        def list_to_dict(action_list: List[str]) -> dict:
            returning_dict = {}
            for action in action_list:
                key = action.replace(" ", "_")
                returning_dict[key] = "None"  # Toml won't work with None
            return returning_dict

        # create dicts from constant actions
        actions = toml.load("app/constant.toml")
        morning_dict = list_to_dict(action_list=actions["morning"])
        evening_dict = list_to_dict(action_list=actions["evening"])
        general_dict = list_to_dict(action_list=actions[day]["general"])
        food_dict = list_to_dict(action_list=actions[day]["food"])

        # create dicts from planned actions, then wipe planned actions
        actions = toml.load("app/planned.toml")
        planned_dict = list_to_dict(action_list=actions["tasks"])
        with open("app/planned.toml", "w") as file:
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
        with open("app/current.toml", "w") as file:
            toml.dump(current_dict, file)

    @classmethod
    def get_flat_current_values(cls) -> list:

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

        dicts = toml.load("app/current.toml")
        _ = dicts.pop("date", None)
        _ = dicts.pop("tomorrow", None)
        return list(extract_nested_values(dicts))

    @classmethod
    def get_score(cls) -> int:
        score = 0
        values = cls.get_flat_current_values()
        for value in values:
            if value != "None":
                score += int(value)
        return score

    @classmethod
    def set_all_action_values(cls, value: int):
        toml_data = toml.load("app/current.toml")
        for section in list(toml_data.keys()):
            if isinstance(toml_data[section], dict):
                for action in list(toml_data[section].keys()):
                    if toml_data[section][action] == "None":
                        toml_data[section][action] = value

        with open("app/current.toml", "w") as file:
            toml.dump(toml_data, file)

    @classmethod
    def get_action_value(cls, section: str, name: str) -> Union[int, str]:
        dicts = toml.load("app/current.toml")
        return dicts[section][name]

    @classmethod
    def set_action_value(cls, section: str, name: str, value: Union[str, int]):
        dicts = toml.load("app/current.toml")
        dicts[section][name] = value
        with open("app/current.toml", "w") as file:
            toml.dump(dicts, file)

    @classmethod
    def get_planned_values(cls) -> list:
        return toml.load("app/planned.toml")["tasks"]

    @classmethod
    def set_planned_values(cls, task_list: list):
        toml_data = toml.load("app/planned.toml")
        toml_data["tasks"] = task_list
        with open("app/planned.toml", "w") as file:
            toml.dump(toml_data, file)

    @classmethod
    def get_progress(cls) -> int:
        return toml.load("app/progress.toml").get("multiplier", 0)

    @classmethod
    def set_progress(cls):
        score = cls.get_score()
        total_score = len(cls.get_flat_current_values())
        multiplier = 1 + (0.01 * (score / total_score))
        toml_data = toml.load("app/progress.toml")
        toml_data["progress"] *= multiplier
        with open("app/progress.toml", "w") as file:
            toml.dump(toml_data, file)
