"""Module for anything cookie related"""

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager


class CookieTools:
    """Class containing useful cookie functions"""

    _COOKIES = None

    @classmethod
    def setup_cookies(cls):
        """Method for setting up the cookie system"""

        cls._COOKIES = EncryptedCookieManager(
            prefix="LukeP81/Day_tracker/",
            password=st.secrets["cookie_password"],
        )
        if not cls._COOKIES.ready():
            # Wait for the component to load and send us current cookies.
            st.stop()

    @classmethod
    def verify_password_cookie(cls) -> bool:
        """Method for verifying the password cookie"""

        # pylint: disable=(unsupported-membership-test)
        # pylint: disable=(unsubscriptable-object))

        if "password" in cls._COOKIES:
            if cls._COOKIES["password"] == st.secrets["password"]:
                return True
        return False

    @classmethod
    def set_password_cookie(cls, password: str):
        """Method for setting the password cookie system"""

        # pylint: disable=(unsupported-assignment-operation)
        cls._COOKIES["password"] = password
        cls._COOKIES.save()
