from pathlib import Path
from typing import NamedTuple, Optional, Union
import logging
import random

import requests
import tomli_w
import tomli

QUOTE_FILE_ADDRESS = "https://raw.githubusercontent.com/Gnomeball/SwackQuote/main/quotes.toml"
QUOTE_FILE_PATH    = Path("quotes.toml") # The collection of all quotes
QUOTE_DUD_PATH     = Path("quote_duds.toml") # Any quotes that aren't `quote_compliant()`
QUOTE_DECK_PATH    = Path("quote_deck.txt") # The current deck of quotes we're using
QUOTE_HISTORY_PATH = Path("quote_history.txt") # The logged appearances of each quote
QUOTE_REPEAT_DELAY = 200 # How many days must pass before a repeated quote should be allowed

# Our Quote type, has optional attribution & source, requires submitter & quote
class Quote(NamedTuple):
    submitter: str
    quote: str
    attribution: Optional[str] = None
    source: Optional[str] = None

def quote_compliant(quote: dict) -> bool:
    """
    Checks whether a dict would make a valid Quote.
    :returns: Is quote a valid Quote?
    :rtype: bool
    """
    if not isinstance(quote, dict): return False # we must start with a dictionary
    for key, val in quote.items():
        if key not in Quote.__annotations__ or not isinstance(val, str):
            return False # field not in Quote or not a str
    if "quote" not in quote and "submitter" not in quote: return False # missing required fields
    if len(quote["quote"]) > 4000: return False # discord has limits
    return True

# def quote_compliant(quote: dict):
#     """
#     Checks whether a dict would make a valid Quote.
#     :returns: Is quote a valid Quote?
#     :rtype: bool
#     """
#     match quote:
#         case {"submitter": str(_), "quote": str(text), **optional} if len(text) < 4000:
#             for key, val in optional.items():
#                 if key not in Quote.__annotations__ or not isinstance(val, str):
#                     return False # field not in Quote or not a str
#             return True
#     return False

def as_quotes(quotes: str) -> tuple[dict[str, Quote], dict[str, Quote]]:
    """
    Converts a TOML-format string to a dict[str, Quote] of identifier -> Quote
    :returns: Dictionary of Quote identifiers to Quote.
    :rtype: dict[str, Quote], dict[str, Quote]
    """
    loaded_quotes = tomli.loads(quotes)
    quote_dict = {i: Quote(**q) for i, q in loaded_quotes.items() if quote_compliant(q)}
    non_compliant = {i: q for i, q in loaded_quotes.items() if not quote_compliant(q)}
    return quote_dict, non_compliant

def as_dicts(quotes: dict[str, Quote]) -> dict[str, dict[str, str]]:
    """
    Converts a dict[str, Quote] to something TOML can serialise.
    :returns: Dictionary of quote identifiers to TOML-compatible dicts
    :rtype: dict[str, dict[str, str]]
    """
    return {
        identifier: {k: v for k, v in quote._asdict().items() if v is not None}
        for identifier, quote in quotes.items()
    }

def calculate_swack_level() -> str:
    """
    Calculate the Swack Level with the Patent-Pending Swack Power Meter
    :returns: An appropriate level of Swack
    :rtype: str
    """
    swack_levels = [
        "Maximum Swack!", "A Modicum of Swack", "Level of Swack: undefined",
        "Possibility of Swack", "Swack mode uninitialised", "All of the Swack",
        "None of the Swack", "The Swackening", "The Swack to end all Swack",
        "The one true Swack", "Just a casual Swack", "One Swack, mildly tepid",
        "Is this the real Swack, or is this just fantasy?", "Hello, Swack!",
        "Not an ounce of Swack in the building", "One Swack; ice and a slice",
        "Am I Swacking correctly?", "Unexpected Loss in the Swacking area",
        "Do you even Swack?", "We're Swacking off at 1PM, right?", "Swack™",
        "Incorrect usage of the Swack!", "Ilicit Swacking Equipment", "Swæk",
        "The Swack are not what they seem", "All your Swack are belong to us",

    ]
    return random.choice(swack_levels)

def format_quote_text(quote: Quote, attribution_only = False) -> str:
    """
    Formats a Quote into our preferred string output.
    :returns: A string containing the quote, it's attribution, and with any affordances we have for accessibility.
    :rtype: str
    """
    quote_text = quote.quote if not attribution_only else ""
    if quote.attribution is not None:
        quote_text += f" ~{quote.attribution}"
    if "'''" not in quote_text:
        quote_text = quote_text.replace(". ", ".  ").replace(".   ", ".  ")
    return quote_text

def pull_specific_quote(quote: str, quotes: dict[str, Quote]) -> tuple[Quote, Union[int, str]]:
    """
    Selects a given quote from the given dictionary.
    :returns: The selected quote, or, failing that, a test quote.
    :rtype: Quote, Union[int, str]
    """
    if quote in quotes:
        return quotes[quote], list(quotes).index(quote) + 1
    else:
        return Quote("Tester", "*Testing* - [Links work too!](https://www.google.co.uk)"), "Test"

def pull_random_quote(quotes: dict[str, Quote]) -> tuple[Quote, int]:
    """
    Selects a random quote from the given dictionary.
    Currently, ignores the last QUOTE_REPEAT_DELAY quotes.
    We reference the deck of current quotes for which are good to use and update it.
    :returns: A Quote(submitter, quote, attribution = None, source = None) and its position in the full list.
    :rtype: Quote, int
    """
    recent = QUOTE_HISTORY_PATH.read_text(encoding = "utf8").splitlines()[-QUOTE_REPEAT_DELAY:]
    rs, deck = set(recent), set(QUOTE_DECK_PATH.read_text(encoding = "utf8").splitlines())
    good_q = [(i, k) for i, k in enumerate(quotes, 1) if k not in rs and k in deck]

    quote_index, quote = random.choice(good_q)
    deck.remove(quote)
    recent.append(quote)

    QUOTE_HISTORY_PATH.write_text("\n".join(recent), encoding = "utf8")
    QUOTE_DECK_PATH.write_text("\n".join(deck - rs), encoding = "utf8")

    return quotes[quote], quote_index

def pull_quotes_from_file() -> tuple[dict[str, Quote], dict[str, Quote]]:
    """
    Pulls the quotes from a local file at QUOTE_FILE_PATH.
    :returns: The dictionary of quotes and a dictionary of not-quite quotes
    :rtype: dict[str, Quote], dict[str, Quote]
    """
    return as_quotes(QUOTE_FILE_PATH.read_text())

def pull_quotes_from_repo() -> tuple[dict[str, Quote], dict[str, Quote]]:
    """
    Pulls updated quotes from the repository.
    :returns: Updated quotes as a dictionary of quotes and a dictionary of not-quite quotes.
    :rtype: dict[str, Quote], dict[str, Quote]
    """
    logger = logging.getLogger("pull_from_repo")
    updated_quotes = ""
    try:
        logger.info(f"Updating quotes from: {QUOTE_FILE_ADDRESS}")
        req = requests.get(QUOTE_FILE_ADDRESS)
        if req.status_code != 200:
            logger.error(f"Failed to get {QUOTE_FILE_ADDRESS} with status: {req.status_code}")
        else:
            updated_quotes = req.text
    except Exception:
        logger.exception("Exception while getting updated quotes:")

    return as_quotes(updated_quotes)

async def refresh_quotes() -> dict[str, Quote]:
    """
    Overwrites QUOTE_FILE_PATH with any updates.
    If we cannot reach the repo, we always fallback to local.
    Probably don't call this one from two different threads.
    :returns: The most up-to-date dict of quotes we can access.
    :rtype: dict[str, Quote]
    """
    logger = logging.getLogger("refresh_quotes")
    quotes, duds = pull_quotes_from_file()
    updated_quotes, updated_duds = pull_quotes_from_repo()
    duds |= updated_duds
    if duds != {}:
        logger.info(f"We have recorded dud quotes to {QUOTE_DUD_PATH}")
        with open(QUOTE_DUD_PATH, "wb") as f:
            tomli_w.dump(as_dicts(duds), f)
    if updated_quotes == {}:
        logger.info(f"{QUOTE_FILE_ADDRESS} was empty")
        return quotes
    if quotes == updated_quotes:
        logger.info(f"{QUOTE_FILE_PATH} and {QUOTE_FILE_ADDRESS} are the same")
        return quotes
    if quotes == {}: logger.info(f"{QUOTE_FILE_PATH} was empty")

    additions = [(k, q) for k, q in updated_quotes.items() if k not in quotes]
    removals  = [(k, q) for k, q in quotes.items() if k not in updated_quotes]
    changed   = [(k, q, quotes[k]) for k, q in updated_quotes.items() if k in quotes and q != quotes[k]]

    for k, (submitter, quote, *opt) in additions:
        logger.info(f"+ [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")
    for k, (submitter, quote, *opt) in removals:
        logger.info(f"- [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")
    for k, (submitter, quote, *opt), (old_s, old_q, *old_opt) in changed:
        logger.info(f"- [{k}] {old_s}{'; '.join(map(str, filter(None, old_opt)))}: {old_q}")
        logger.info(f"+ [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")

    if quotes != updated_quotes:
        with open(QUOTE_FILE_PATH, "wb") as f:
            tomli_w.dump(as_dicts(updated_quotes), f)

    deck = set(QUOTE_DECK_PATH.read_text(encoding = "utf8").splitlines())
    if deck:
        deck -= {k for k, _ in removals}
        deck |= {k for k, _ in additions}
    else:
        deck.update(updated_quotes) # cycle deck, filling it back up again

    QUOTE_DECK_PATH.write_text("\n".join(deck), encoding = "utf8")

    return updated_quotes
