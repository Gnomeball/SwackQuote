from collections import namedtuple
from pathlib import Path
import random
import requests
import logging
import asyncio
import tomli
import tomli_w

QUOTE_FILE_ADDRESS = 'https://raw.githubusercontent.com/Gnomeball/SwackQuote/main/quotes.toml'
QUOTE_FILE_PATH    = "quotes.toml" # The collection of all quotes
QUOTE_DUD_PATH     = "quote_duds.toml" # Any quotes that aren't `quote_compliant()`
QUOTE_DECK_PATH    = "quote_deck.txt" # The current deck of quotes we're using
QUOTE_HISTORY_PATH = "quote_history.txt" # The logged appearances of each quote
QUOTE_REPEAT_DELAY = 200 # How many days must pass before a repeated quote should be allowed

# Our Quote type, has optional attribution & source, requires submitter, & quote
Quote = namedtuple("Quote", "submitter quote attribution source", defaults=(None, None))

def quote_compliant(quote: dict):
  pass

def as_quotes(quotes: str):
  """
  Converts a TOML-format string to a dict[str, Quote] of identifier -> Quote
  :returns: Dictionary of Quote identifiers to Quote.
  :rtype: dict[str, Quote]
  """
  # TODO: handle incorrectly formatted quotes, preferably by putting a new embed on discord
  # so should log to a file, and then when bot.py runs it has a subroutine to check it and send a message
  return {identifier: Quote(**quote) for identifier, quote in tomli.loads(quotes).items()}

def calculate_swack_level():
    swack_levels = [
        "Maximum Swack!", "A Modicum of Swack", "Level of Swack: undefined",
        "Possibility of Swack", "Swack mode uninitialised", "All of the Swack",
        "None of the Swack", "The Swackening", "The Swack to end all Swack",
        "The one true Swack", "Just a casual Swack", "One Swack, mildly tepid",
        "Is this the real Swack, or is this just fantasy?", "Hello, Swack!",
        "Not an ounce of Swack in the building", "Am I Swacking correctly?"
    ]
    # Idk if this way round is better than rotate then shuffle
    # random.shuffle(swack_levels)
    # rotate = random.randint(0, len(swack_levels))
    # swack_levels = swack_levels[rotate:] + swack_levels[:rotate]
    return random.choice(swack_levels) # random.choice() is plenty random enough, "mixing randomness" doesn't help here

def format_quote_text(quote: Quote):
    quote_text = quote.quote
    if quote.attribution is not None:
        quote_text += f" ~{quote.attribution}"
    if "'''" not in quote_text:
        quote_text = quote_text.replace(". ", ".  ").replace(".   ", ".  ")
    return quote_text

def pull_specific_quote(quote: str, quotes: dict):
    """
    Selects a given quote from the given dictionary.
    :returns: A Quote(submitter="Tester", quote="*Testing* - [Links work too!](https://www.google.co.uk)", attribution=None, source=None).
    :rtype: Quote
    """
    return (quotes[quote], list(quotes.keys()).index(quote)+1) if quote in quotes else (Quote("Tester", "*Testing* - [Links work too!](https://www.google.co.uk)"), "Test")
    # return quotes[quote] if quote in quotes else Quote("Tester", "*Testing* - [Links work too!](https://www.google.co.uk)")

def pull_random_quote(quotes: dict):
    """
    Selects a random quote from the given dictionary.
    Currently, ignores the last QUOTE_REPEAT_DELAY quotes.
    We reference the deck of current quotes for which are good to use and update it.
    :returns: A Quote(submitter, quote, attribution=None, source=None) and its position in the full list.
    :rtype: Quote, int
    """
    with open(QUOTE_DECK_PATH, "r", encoding="utf8") as d:
        deck = set(map(str.strip, d.readlines()))

    with open(QUOTE_HISTORY_PATH, "r", encoding="utf8") as f:
        recent = set(map(str.strip, f.readlines()[-QUOTE_REPEAT_DELAY:]))
        good_q = [(i,k) for i,k in enumerate(quotes.keys(), 1) if k not in recent and k in deck]

    random.shuffle(good_q)
    quote_index, quote = random.choice(good_q)
    deck.remove(quote)

    with open(QUOTE_HISTORY_PATH, "a", encoding="utf8", newline="\n") as f:
        f.write(f"{quote}\n")
    with open(QUOTE_DECK_PATH, "w+", encoding="utf8", newline="\n") as d:
        d.write("\n".join(deck-recent))

    return quotes[quote], quote_index

def pull_quotes_from_file(path=QUOTE_FILE_PATH):
    """
    Pulls the quotes from a local file (default: "quotes.toml").
    :returns: The dictionary of quotes.
    :rtype: dict[str, Quote]
    """
    return as_quotes(Path(path).read_text(encoding="utf8"))

def pull_quotes_from_repo():
    """
    Pulls updated quotes from the repository.
    :returns: Updated quotes as a dictionary of quotes.
              On error, returns an empty list and logs exception.
    :rtype: dict[str, Quote]
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

async def refresh_quotes():
    """
    Overwrites quotes.txt with any updates.
    If we cannot reach the repo, we always fallback to local.
    Probably don't call this one from two different threads.
    :returns: The most up-to-date dict of quotes we can access.
    :rtype: dict[str, Quote]
    """
    logger = logging.getLogger("refresh_quotes")
    quotes = pull_quotes_from_file()
    updated_quotes = pull_quotes_from_repo()
    if updated_quotes == {}: return quotes

    additions = [q for k,q in updated_quotes.items() if k not in quotes]
    removals  = [q for k,q in quotes.items() if k not in updated_quotes]
    changed   = [(q, quotes[k]) for k,q in updated_quotes.items() if k in quotes and q != quotes[k]]

    for submitter,quote,*opt in additions:
        logger.info(f"+ {submitter} ({' '.join(map(str,opt))}) {quote}")
    for submitter,quote,*opt in removals:
        logger.info(f"- {submitter} ({' '.join(map(str,opt))}) {quote}")
    for (submitter,quote,*opt), (old_s,old_q,*old_opt) in changed:
        logger.info(f"+ {submitter} ({' '.join(map(str,opt))}) {quote}")
        logger.info(f"- {old_s} ({' '.join(map(str,old_opt))}) {old_q}")

    if quotes != updated_quotes:
        with open(QUOTE_FILE_PATH, "wb") as f:
            tomli_w.dump(updated_quotes, f)
    with open(QUOTE_DECK_PATH, "w+", encoding="utf8", newline="\n") as d:
        deck = set(map(str.split, d.readlines()))
        if len(deck) == 0: # Cycle deck, filling it back up again
            d.write("\n".join(updated_quotes.keys()))
        else:
            deck |= {q.quote for q in additions}
            deck -= {q.quote for q in removals}
            d.write("\n".join(deck))
    return updated_quotes
