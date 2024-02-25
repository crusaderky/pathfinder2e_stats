"""TODO

A module that lets you say Hello world
"""
from __future__ import annotations


def hello(french: bool = False) -> str:
    """Say hello world!

    :param bool french:
        If True, speak in French. If False, speak in English.
    :return:
        A string greeting the user
    :rtype:
        str
    """
    if french:
        return "Bonjour, Monde!"
    else:
        return "Hello, World!"
