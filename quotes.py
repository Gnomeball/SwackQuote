"""
A polite little Discord bot that can send out a quote each day.

`quotes.py` focuses on parsing, formatting, and updating quotes.
"""

import logging
import random
import tomllib
from pathlib import Path
from typing import Any, NamedTuple

import requests
import tomli_w

QUOTE_FILE_ADDRESS = "https://raw.githubusercontent.com/Gnomeball/SwackQuote/main/quotes.toml"
"Where to check for the latest quotes."

LOCAL_DIR = Path(__file__).parent.resolve()
"Where this file and other files are placed"

QUOTE_FILE_PATH = LOCAL_DIR / "quotes.toml"
"The collection of all quotes."

QUOTE_DUD_PATH = LOCAL_DIR / "quote_duds.toml"
"Any quotes that aren't `quote_compliant()`."

QUOTE_DECK_PATH = LOCAL_DIR / "quote_deck.txt"
"The current deck of quotes we're using."

QUOTE_HISTORY_PATH = LOCAL_DIR / "quote_history.txt"
"The logged appearances of each quote."

QUOTE_REPEAT_DELAY = 200
"How many days must pass before a repeated quote should be allowed."

DISCORD_MESSAGE_LENGTH_LIMIT = 4000
"How long can a Discord message be? This long, give or take."


class Quote(NamedTuple):
    """Our Quote type, bundles its info together, requires submitter & quote."""

    submitter: str
    quote: str
    attribution: str | None = None
    source: str | None = None
    embed: bool = False


def quote_compliant(quote: dict) -> bool:
    """
    Checks whether a dict would make a valid Quote.

    :returns: Is quote a valid Quote?
    :rtype: bool
    """
    logger = logging.getLogger("quote_compliant")
    annos = Quote.__annotations__
    "Type annotations for Quote, {field: [types]} map."
    required_fields = {field for field in annos if field not in Quote._field_defaults}
    "Necessary fields that must be supplied for a Quote."
    match quote:
        case dict(quote):
            well_formed_quote = True
            """Whether the quote is good to go."""

            for field in required_fields:
                if field not in quote:
                    logger.error(f"Missing '{field}' field from quote {quote}")
                    well_formed_quote = False

            for key, val in quote.items():
                match key, val:
                    case "submitter" | "quote", str():
                        logger.debug(f"Field {key} = {val} (str)")
                    case "attribution" | "source", str() | None:
                        logger.debug(f"Field {key} = {val} ({type(val)})")
                    case "embed", bool():
                        logger.debug(f"Field {key} = {val} (bool)")
                    case "submitter" | "quote" | "attribution" | "source" | "embed", _:
                        logger.error(f"Field {key} is an incorrect type, must be {annos[key]}, was {type(val)}({val})")
                        well_formed_quote = False
                    case _, _:
                        logger.error(f"{key} is not valid field for Quote, must be one of {', '.join(annos)}")
                        well_formed_quote = False

            if len(quote["quote"]) > DISCORD_MESSAGE_LENGTH_LIMIT:
                logger.error(
                    f"Quote is too long, must be less than 4000 bytes (UTF-8), but is {len(quote['quote'])} bytes long"
                )
                well_formed_quote = False

            return well_formed_quote
        case _:
            logger.error(f"Quote must be a dictionary, was {type(quote)}({quote})")
            return False


def as_quotes(quotes: str, logger: logging.Logger) -> tuple[dict[str, Quote], dict[str, dict[str, Any]]]:
    """
    Converts a TOML-format string to a dict[str, Quote] of identifier -> Quote.

    :returns: Dictionary of Quote identifiers to Quote.
    :rtype: dict[str, Quote], dict[str, Quote]
    """
    loaded_quotes = tomllib.loads(quotes)
    quote_dict, non_compliant = {}, {}
    for i, q in loaded_quotes.items():
        if quote_compliant(q):
            quote_dict[i] = Quote(**q)
        else:
            non_compliant[i] = q
    if len(non_compliant):
        logger.error(f"Received non compliant quotes:\n {non_compliant}")
    return quote_dict, non_compliant


def as_dicts(quotes: dict[str, Quote]) -> dict[str, dict[str, str]]:
    """
    Converts a dict[str, Quote] to something TOML can serialise.

    :returns: Dictionary of quote identifiers to TOML-compatible dicts
    :rtype: dict[str, dict[str, str]]
    """
    return {
        identifier: {k: v for k, v in quote._asdict().items() if v is not None} for identifier, quote in quotes.items()
    }


def calculate_swack_level() -> str:
    """
    Calculate the Swack Level with the Patent-Pending Swack Power Meter!

    :returns: An appropriate level of Swack
    :rtype: str
    """
    swack_levels = [
        "Maximum Swack!",
        "A Modicum of Swack",
        "Level of Swack: undefined",
        "Possibility of Swack",
        "Swack mode uninitialised",
        "All of the Swack",
        "None of the Swack",
        "The Swackening",
        "The Swack to end all Swack",
        "The one true Swack",
        "Just a casual Swack",
        "One Swack, mildly tepid",
        "Is this the real Swack, or is this just fantasy?",
        "Hello, Swack!",
        "Not an ounce of Swack in the building",
        "One Swack; ice and a slice",
        "Am I Swacking correctly?",
        "Unexpected Loss in the Swacking area",
        "Do you even Swack?",
        "We're Swacking off at 1PM, right?",
        "Swack™",
        "Incorrect usage of the Swack!",
        "Ilicit Swacking Equipment",
        "Swæk",
        "The Swack are not what they seem",
        "All your Swack are belong to us",
        "Swacked, not stirred",
    ]
    return random.choice(swack_levels)


def format_quote_text(quote: Quote) -> str:
    """
    Formats a Quote into our preferred string output.

    :returns: A string containing the quote, its attribution, and with any affordances we have for accessibility.
    :rtype: str
    """
    quote_text = quote.quote
    if quote.attribution is not None:
        quote_text += f" ~{quote.attribution}"
    if "'''" not in quote_text:
        quote_text = quote_text.replace(". ", ".  ").replace(".   ", ".  ")
    return quote_text


def pull_specific_quote(quote: str, quotes: dict[str, Quote]) -> tuple[Quote, int | str]:
    """
    Selects a given quote from the given dictionary.

    :returns: The selected quote, or, failing that, a test quote.
    :rtype: Quote, Union[int, str]
    """
    if quote in quotes:
        return quotes[quote], list(quotes).index(quote) + 1

    return Quote("Tester", "*Testing* - [Links work too!](https://www.google.co.uk)"), "Test"


def pull_random_quote(quotes: dict[str, Quote]) -> tuple[Quote, int]:
    """
    Selects a random quote from the given dictionary.

    Currently, ignores the last QUOTE_REPEAT_DELAY quotes.
    We reference the deck of current quotes for which are good to use and update it.
    :returns: A Quote(submitter, quote, attribution = None, source = None) and its position in the full list.
    :rtype: Quote, int
    """
    recent = QUOTE_HISTORY_PATH.read_text(encoding="utf8").splitlines()[-QUOTE_REPEAT_DELAY:]
    rs, deck = set(recent), current_deck()
    good_q = [(i, k) for i, k in enumerate(quotes, 1) if k not in rs and k in deck]

    quote_index, quote = random.choice(good_q)
    deck.remove(quote)
    recent.append(quote)

    QUOTE_HISTORY_PATH.write_text("\n".join(recent), encoding="utf8")
    QUOTE_DECK_PATH.write_text("\n".join(deck - rs), encoding="utf8")

    return quotes[quote], quote_index


def pull_quotes_from_file() -> tuple[dict[str, Quote], dict[str, dict[str, Any]]]:
    """
    Pulls the quotes from a local file at QUOTE_FILE_PATH.

    :returns: The dictionary of quotes and a dictionary of not-quite quotes
    :rtype: dict[str, Quote], dict[str, Quote]
    """
    return as_quotes(QUOTE_FILE_PATH.read_text(), logging.getLogger("pull_quotes_from_file"))


def pull_quotes_from_repo() -> tuple[dict[str, Quote], dict[str, dict[str, Any]]]:
    """
    Pulls updated quotes from the repository.

    :returns: Updated quotes as a dictionary of quotes and a dictionary of not-quite quotes.
    :rtype: dict[str, Quote], dict[str, Quote]
    """
    logger = logging.getLogger("pull_quotes_from_repo")
    updated_quotes = ""
    try:
        logger.info(f"Updating quotes from: {QUOTE_FILE_ADDRESS}")
        req = requests.get(QUOTE_FILE_ADDRESS, timeout=10)
        if req.status_code != 200:
            logger.error(f"Failed to get {QUOTE_FILE_ADDRESS} with status: {req.status_code}")
        else:
            updated_quotes = req.text
    except Exception:
        logger.exception("Exception while getting updated quotes:")

    return as_quotes(updated_quotes, logger)


def current_deck() -> set[str]:
    """Get the deck of quotes we can use next."""
    deck = set(QUOTE_DECK_PATH.read_text(encoding="utf8").splitlines())
    if not deck:
        quotes, _ = pull_quotes_from_file()
        deck.update(quotes)
        QUOTE_DECK_PATH.write_text("\n".join(deck), encoding="utf8")
    return deck


async def refresh_quotes() -> dict[str, Quote]:
    """
    Overwrites QUOTE_FILE_PATH with any updates.

    If we cannot reach the repo, we always fallback to local.
    Probably don't call this one from two different threads.
    :returns: The most up-to-date dict of quotes we can access.
    :rtype: dict[str, Quote]
    """
    logger = logging.getLogger("refresh_quotes")
    deck = current_deck()
    quotes, duds = pull_quotes_from_file()
    updated_quotes, updated_duds = pull_quotes_from_repo()
    duds |= updated_duds
    if len(duds):
        logger.error(f"We have {len(duds)} dud quotes, adding to {QUOTE_DUD_PATH}")
        with QUOTE_DUD_PATH.open("wb") as f:
            tomli_w.dump(duds, f)
    if updated_quotes == {}:
        logger.info(f"{QUOTE_FILE_ADDRESS} was empty")
        return quotes
    if quotes == updated_quotes:
        logger.info(f"{QUOTE_FILE_PATH} and {QUOTE_FILE_ADDRESS} are the same")
        return quotes
    if quotes == {}:
        logger.info(f"{QUOTE_FILE_PATH} was empty")

    additions = [(k, q) for k, q in updated_quotes.items() if k not in quotes]
    removals = [(k, q) for k, q in quotes.items() if k not in updated_quotes]
    changed = [(k, q, quotes[k]) for k, q in updated_quotes.items() if k in quotes and q != quotes[k]]

    for k, (submitter, quote, *opt) in additions:
        logger.info(f"+ [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")
    for k, (submitter, quote, *opt) in removals:
        logger.info(f"- [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")
    for k, (submitter, quote, *opt), (old_s, old_q, *old_opt) in changed:
        logger.info(f"- [{k}] {old_s}{'; '.join(map(str, filter(None, old_opt)))}: {old_q}")
        logger.info(f"+ [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")

    if quotes != updated_quotes:
        with QUOTE_FILE_PATH.open("wb") as f:
            tomli_w.dump(as_dicts(updated_quotes), f)

    deck -= {k for k, _ in removals}
    deck |= {k for k, _ in additions}
    QUOTE_DECK_PATH.write_text("\n".join(deck), encoding="utf8")

    return updated_quotes
