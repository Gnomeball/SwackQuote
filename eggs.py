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


LOCAL_DIR = Path(__file__).parent.resolve()


EGGS = LOCAL_DIR / "eggs.toml"
"Eggs, of the Easter variety."


class Egg(NamedTuple):
    """Eggs, of the Easter variety"""

    quote_id: str
    quote_num: int
    notes: str | None = None


def egg_hunting() -> dict[str, Egg]:
    """
    Goes Egg hunting.

    :returns: A basket of sorted Eggs.
    :rtype: dict[str, Egg]
    """
    raw_eggs = tomllib.loads(EGGS.read_text(encoding="utf8"))
    # There is a better way to do this.. it sucks!
    eggs = {}
    for egg in raw_eggs:
        eggs[egg] = Egg(**raw_eggs[egg])
    return eggs
