"""Module containing the classes for housing tasks"""

import streamlit as st

from toml_tools import TomlTools


class BasicObjective:
    """Basic class for housing a task"""

    def __init__(self, section: str, name: str):
        """Constructor method for the class"""

        self._section = section
        self._name = name
        self._value = TomlTools.get_action_value(section=section, name=name)

    def _extra_method(self):
        """Private method for subclassing,
        included here so the _to_do_display does not need to be
        rewritten when subclassing
        """

        pass

    def _to_do_display(self):
        """Private method for displaying a task yet to be done"""

        with st.form(key=f"{self._section}_{self._name}"):
            st.subheader(self._name)
            self._extra_method()
            left, middle, right = st.columns(3)
            good = left.form_submit_button(label="Actioned")
            medium = middle.form_submit_button(label="Undoable")
            bad = right.form_submit_button(label="Avoided")
        if good:
            TomlTools.set_action_value(section=self._section, name=self._name,
                                       value=1)
        elif medium:
            TomlTools.set_action_value(section=self._section, name=self._name,
                                       value=0)
        elif bad:
            TomlTools.set_action_value(section=self._section, name=self._name,
                                       value=-1)
        if any([good, medium, bad]):
            st.experimental_rerun()

    def _done_display(self):
        """Private method for displaying a task that had been done"""

        message, undo = st.columns(2)
        message_dict = {
            1: st.success,
            0: st.warning,
            -1: st.error,
        }
        with message:
            message_dict[self._value](self._name)
        perform_undo = undo.button(label="Undo",
                                   key=f"undo_{self._section}_{self._name}")
        if perform_undo:
            TomlTools.set_action_value(section=self._section, name=self._name,
                                       value="None")
            st.experimental_rerun()

    def display(self):
        """Method for displaying a task"""

        if self._value == "None":
            self._to_do_display()
        else:
            self._done_display()


class WriteObjective(BasicObjective):
    """Class for housing a task that will contain an extra bit of text
    underneath the name
    """

    def __init__(self, section: str, name: str, to_write: str):
        """Constructor method for the subclass"""

        super().__init__(section, name)
        self._to_write = to_write

    def _extra_method(self):
        """Redefining of base class method
        redefined to write a string to underneath the task name
        """

        st.write(self._to_write)


class PlanObjective(BasicObjective):
    """Class for housing a task that will contain a text area for
    entering a list of values underneath the name
    """

    def _to_do_display(self):
        """Redefining of base class method
        redefined to include a text area for
        entering a list of values underneath the name
        """

        with st.form(key=f"{self._section}_{self._name}"):
            st.subheader(self._name)
            current_planned = TomlTools.get_planned_values()
            planned_string = "\n".join(current_planned)
            entered = st.text_area(label="Tomorrow's tasks",
                                   value=planned_string)
            submit = st.form_submit_button(label="Actioned")

        if submit:
            TomlTools.set_action_value(section=self._section, name=self._name,
                                       value=1)
            created_tasks = list(
                {task for task in entered.split("\n") if task})

            TomlTools.set_planned_values(task_list=created_tasks)
            st.experimental_rerun()
