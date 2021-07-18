import random
import requests
import logging
import asyncio

QUOTE_FILE_ADDRESS = 'https://raw.githubusercontent.com/Gnomeball/QuoteBotRepo/main/quotes.txt'

def pull_random_quote(quotes):
    """
    Selects a random quote from the given list.
    Currently, ignores the last 100 quotes that appear in "quote_history.txt".
    :returns: A (submitter, quote) pair.
    :rtype: Tuple[str,str]
    """
    all_q = set(range(1, len(quotes)+1)) # This way the index stuff is entirely internal.

    with open("quote_history.txt", "r") as f:
        good_q = sorted(all_q - set(map(int, f.read().splitlines()[-100:])))

    random.shuffle(good_q) # shortlisting has no effect since we always pick one successfully
    quote = random.choice(good_q)

    with open("quote_history.txt", "a") as f:
        f.write(f"{quote}\n")

    return quotes[quote]

def parse_quotes(lst):
    """
    Parse (submitter, quote) pairs from a given list of strings.
    The format is currently `submitter###quote`.
    TODO: Multiline quote support.
    :returns: A list of parsed (submitter, quote) pairs.
    :rtype: List[Tuple[str,str]]
    """
    return [tuple(quote.split("###", maxsplit = 1)) for quote in lst]

def pull_quotes_from_file(path="quotes.txt"):
    """
    Pulls the quotes from a local file (default: "quotes.txt").
    :returns: The list of (submitter, quote) pairs from the file.
    :rtype: List[Tuple[str,str]]
    """
    with open(path, "r") as f:
        return parse_quotes(f.read().splitlines())

def pull_quotes_from_repo():
    """
    Pulls updated quotes from the repository.
    :returns: Updated quotes as a list of (submitter, quote) pairs.
              On error, returns an empty list and logs exception.
    :rtype: List[Tuple[str,str]]
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
    return parse_quotes(updated_quotes.splitlines())

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
    if updated_quotes == []:
        return quotes
    # calc & pretty-print diff to log in a horrible way; cpu go brrr
    additions = [q for q in updated_quotes if q not in quotes]
    removals  = [q for q in quotes if q not in updated_quotes]
    for submitter,quote in additions:
        logger.info(f"+ {submitter} {quote}")
    for submitter,quote in removals:
        logger.info(f"- {submitter} {quote}")

    if quotes != updated_quotes:
        flattened_quotes = "\n".join([f"{submitter}###{quote}" for submitter,quote in updated_quotes])
        with open("quotes.txt", "w") as f:
            f.write(flattened_quotes)
    return updated_quotes
