from collections import namedtuple
from pathlib import Path
import random
import logging

import tomli
import tomli_w
import requests

QUOTE_FILE_ADDRESS = 'https://raw.githubusercontent.com/Gnomeball/SwackQuote/main/quotes.toml'
QUOTE_FILE_PATH    = "quotes.toml" # The collection of all quotes
QUOTE_DUD_PATH     = "quote_duds.toml" # Any quotes that aren't `quote_compliant()`
QUOTE_DECK_PATH    = "quote_deck.txt" # The current deck of quotes we're using
QUOTE_HISTORY_PATH = "quote_history.txt" # The logged appearances of each quote
QUOTE_REPEAT_DELAY = 200 # How many days must pass before a repeated quote should be allowed

# Our Quote type, has optional attribution & source, requires submitter, & quote
Quote = namedtuple("Quote", "submitter quote attribution source", defaults = (None, None))

def quote_compliant(quote: dict):
  """
  Checks whether a dict would make a valid Quote.
  :returns: Is quote a valid Quote?
  :rtype: bool
  """
  if not isinstance(quote, dict): return False # no top-level variables allowed
  if set(quote).difference(Quote._fields): return False # has bad keys
  if not all(isinstance(v, str) for v in quote.values()): return False # has bad values
  if "quote" not in quote and "submitter" not in quote: return False # missing required fields
  if len(quote["quote"]) > 4000: return False # discord has limits
  return True

def as_dicts(quotes: dict[str, Quote]):
  """
  Converts a dict[str, Quote] to something TOML can serialise.
  :returns: Dictionary of quote identifiers to TOML-compatible dicts
  :rtype: dict[str, dict[str, str]]
  """
  return {i: {k: v for k, v in q._asdict().items() if v is not None} for i, q in quotes.items()}

def as_quotes(quotes: str):
  """
  Converts a TOML-format string to a dict[str, Quote] of identifier -> Quote
  :returns: Dictionary of Quote identifiers to Quote, and those that were not.
  :rtype: dict[str, Quote], dict[str, dict[str, Any]]
  """
  loaded_quotes = tomli.loads(quotes)
  quote_dict = {i: Quote(**q) for i, q in loaded_quotes.items() if quote_compliant(q)}
  non_compliant = {i: q for i, q in loaded_quotes.items() if i not in quote_dict}
  return quote_dict, non_compliant

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
    :returns: The dictionary of quotes and a dictionary of not-quite quotes
    :rtype: dict[str, Quote], dict[str, dict[str, Any]]
    """
    return as_quotes(Path(path).read_text(encoding="utf8"))

def pull_quotes_from_repo():
    """
    Pulls updated quotes from the repository.
    :returns: Updated quotes as a dictionary of quotes and a dictionary of not-quite quotes.
    :rtype: dict[str, Quote], dict[str, dict[str, Any]]
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

    additions = [(k, q) for k,q in updated_quotes.items() if k not in quotes]
    removals  = [(k, q) for k,q in quotes.items() if k not in updated_quotes]
    changed   = [(k, q, quotes[k]) for k,q in updated_quotes.items() if k in quotes and q != quotes[k]]

    for k, (submitter,quote,*opt) in additions:
        logger.info(f"+ [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")
    for k, (submitter,quote,*opt) in removals:
        logger.info(f"- [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")
    for k, (submitter,quote,*opt), (old_s,old_q,*old_opt) in changed:
        logger.info(f"- [{k}] {old_s}{'; '.join(map(str, filter(None, old_opt)))}: {old_q}")
        logger.info(f"+ [{k}] {submitter}{'; '.join(map(str, filter(None, opt)))}: {quote}")

    if quotes != updated_quotes:
        with open(QUOTE_FILE_PATH, "wb") as f:
            tomli_w.dump(as_dicts(updated_quotes), f)
    with open(QUOTE_DECK_PATH, "w+", encoding="utf8", newline="\n") as d:
        deck = set(map(str.split, d.readlines()))
        if len(deck) == 0: # Cycle deck, filling it back up again
            d.write("\n".join(updated_quotes.keys()))
        else:
            deck |= {q.quote for q in additions}
            deck -= {q.quote for q in removals}
            d.write("\n".join(deck))
    return updated_quotes
