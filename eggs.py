"""
A polite little Discord bot that can send out a quote each day.

`eggs.py` handles the eggs.
"""

# import logging
# import random
import tomllib
from pathlib import Path
from typing import Any, NamedTuple

# import requests
import tomli_w


EGGS = LOCAL_DIR / "eggs.toml"
"Eggs, of the Easter variety."


class Egg(NamedTuple):
    """Eggs, of the Easter variety"""

    quote_id: str
    quote_num: str
    notes: str | None = None


def egg_hunting() -> set[str]:
    """Goes Egg hunting."""
    eggs = set(EGGS.read_text(encoding="uft8").splitlines())
    return eggs


def egg_sorting() -> dict[str, Egg]:
    """Sorts the Eggs."""
    # create and return a dictionary of eggs, from the set collected above