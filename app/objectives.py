import streamlit as st

from app.toml_tools import TomlTools


class BasicObjective:
    def __init__(self, section: str, name: str):
        self._section = section
        self._name = name
        self._value = TomlTools.get_action_value(section=section, name=name)

    def _extra_method(self):
        pass

    def _to_do_display(self):
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
        if self._value == "None":
            self._to_do_display()
        else:
            self._done_display()


class WriteObjective(BasicObjective):
    def __init__(self, section: str, name: str, to_write: str):
        super().__init__(section, name)
        self._to_write = to_write

    def _extra_method(self):
        st.write(self._to_write)


class PlanObjective(BasicObjective):

    def _to_do_display(self):
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
            created_tasks = list(set([
                task for task in entered.split("\n") if task])
            )
            TomlTools.set_planned_values(task_list=created_tasks)
            st.experimental_rerun()
