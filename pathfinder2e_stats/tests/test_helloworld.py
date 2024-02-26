from __future__ import annotations

# TODO
from pathfinder2e_stats.helloworld import hello


def test_hello():
    assert hello() == "Hello, World!"
    assert hello(french=True) == "Bonjour, Monde!"
