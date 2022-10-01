import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager


class CookieTools:
    _COOKIES = None

    @classmethod
    def setup_cookies(cls):
        cls._COOKIES = EncryptedCookieManager(
            prefix="LukeP81/Day_tracker/",
            password=st.secrets["cookie_password"],
        )
        if not cls._COOKIES.ready():
            # Wait for the component to load and send us current cookies.
            st.stop()

    @classmethod
    def verify_password_cookie(cls) -> bool:
        # pylint: disable=(unsupported-membership-test)
        # pylint: disable=(unsubscriptable-object))

        if "password" in cls._COOKIES:
            if cls._COOKIES["password"] == st.secrets["password"]:
                return True
        return False

    @classmethod
    def set_password_cookie(cls, password: str):
        # pylint: disable=(unsupported-assignment-operation)
        cls._COOKIES["password"] = password
        cls._COOKIES.save()
