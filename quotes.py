from collections import namedtuple
import random
import requests
import logging
import asyncio
import toml

QUOTE_FILE_ADDRESS = 'https://raw.githubusercontent.com/Gnomeball/QuoteBotRepo/main/quotes.toml'

# Our Quote type, has optional attribution & source, requires submitter & quote
Quote = namedtuple("Quote", "submitter quote attribution source", defaults=(None, None))

def pull_random_quote(quotes: dict):
    """
    Selects a random quote from the given dictionary.
    Currently, ignores the last 100 quotes logged in "quote_history.txt".
    :returns: A Quote(submitter, quote, attribution=None, source=None).
    :rtype: Quote
    """
    with open("quote_history.txt", "r") as f:
        recent = set(map(str.strip, f.readlines()[-100:]))
        good_q = [k for k in quotes.keys() if k not in recent]

    random.shuffle(good_q)
    quote = random.choice(good_q)

    with open("quote_history.txt", "a") as f:
        f.write(f"{quote}\n")

    return Quote(**quotes[quote])

def pull_quotes_from_file(path="quotes.toml"):
    """
    Pulls the quotes from a local file (default: "quotes.toml").
    :returns: The dictionary of quotes (use Quote(**dict[k])).
    :rtype: Dict
    """
    with open(path, "r", encoding="utf8") as f:
        return toml.load(f)

def pull_quotes_from_repo():
    """
    Pulls updated quotes from the repository.
    :returns: Updated quotes as a dictionary of quotes (use Quote(**dict[k])).
              On error, returns an empty list and logs exception.
    :rtype: Dict
    """
    logger = logging.getLogger("pull_from_repo")
    updated_quotes = ""
    try:
        logger.info(f"Updating quotes from: {QUOTE_FILE_ADDRESS}")
        req = requests.get(QUOTE_FILE_ADDRESS)
        # error codes don't throw exceptions, for some reason
        if req.status_code != 200:
            logger.error(f"Failed to get {QUOTE_FILE_ADDRESS} with status: {req.status_code}")
        else: updated_quotes = req.text
    except Exception:
        logger.exception("Exception while getting updated quotes:")
    
    return toml.loads(updated_quotes)

async def refresh_quotes():
    """
    Overwrites quotes.txt with potentially updated ones.
    If we cannot reach the repo, we always fallback to local.
    Probably don't call this one from two different threads.
    :returns: The most up-to-date set of quotes we can access.
    :rtype: List[Tuple[str,str]]
    """
    logger = logging.getLogger("refresh_quotes")
    quotes = pull_quotes_from_file()
    updated_quotes = pull_quotes_from_repo()
    if updated_quotes == {}: return quotes
    
    additions = [Quote(**q) for k,q in updated_quotes.items() if k not in quotes]
    removals  = [Quote(**q) for k,q in quotes.items() if k not in updated_quotes]
    changed   = [(Quote(**q),Quote(**quotes[k])) for k,q in updated_quotes.items() if k in quotes and Quote(**q)!=Quote(**quotes[k])]
    
    for submitter,quote,*opt in additions:
        logger.info(f"+ {submitter} ({' '.join(opt)}) {quote}")
    for submitter,quote,*opt in removals:
        logger.info(f"- {submitter} ({' '.join(opt)}) {quote}")
    for (submitter,quote,*opt), (old_s,old_q,*old_opt) in changed:
        logger.info(f"+ {submitter} ({' '.join(opt)}) {quote}")
        logger.info(f"- {old_s} ({' '.join(old_opt)}) {old_q}")

    if quotes != updated_quotes:
        with open("quotes.txt", "w") as f:
            toml.dump(updated_quotes, f)
    return updated_quotes
