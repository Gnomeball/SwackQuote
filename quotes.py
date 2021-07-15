import random
import requests
import logging
import asyncio

QUOTE_FILE_ADDRESS = 'https://raw.githubusercontent.com/Gnomeball/QuoteBotRepo/main/quotes.txt'

def pull_random_quote():
    with open("quotes.txt", "r") as f:
        all_q = set(range(1, len(f.read().splitlines()) +1))

    with open("quote_history.txt", "r") as f:
        good_q = sorted(all_q - set(map(int, f.read().splitlines()[-100:])))

    random.shuffle(good_q)
    shortlist = random.sample(good_q, 50)

    random.shuffle(shortlist)
    quote = random.choice(shortlist)

    with open("quote_history.txt", "a") as f:
        f.write(f"{quote}\n")

    return quote


def pull_quotes_from_repo():
    """
    Pulls updated quotes from the repository.
    :returns: An updated quotes.txt as a list of strings.
              On error, returns an empty string and logs exception.
    :rtype: List[str]
    """
    logger = logging.getLogger("pull_from_repo")
    updated_quotes: str = ''
    try:
        logger.info(f"Updating quotes from: {QUOTE_FILE_ADDRESS}")
        req = requests.get(QUOTE_FILE_ADDRESS)
        # error codes don't throw exceptions, for some reason
        if req.status_code != 200:
            logger.error(f"Failed to get {QUOTE_FILE_ADDRESS} with status: {req.status_code}")
        else:
            updated_quotes = req.text
    except Exception:
        logger.exception("Exception while getting updated quotes:")
    return [quote.split("###", maxsplit=1) for quote in updated_quotes.splitlines()]


async def refresh_quotes(quotes=None):
    """
    Refreshes quotes with potentially updated ones.
    Edits quotes in-place.
    Probably don't call this one from two different threads.
    :param quotes: Reference to an existing list of quotes
    :type quotes: List[str]
    :returns: None
    """
    logger = logging.getLogger("refresh_quotes")
    updated_quotes = pull_quotes_from_repo()
    if not updated_quotes:
        return
    # calc & pretty-print diff to log in a horrible way; cpu go brrr
    additions = [q for q in updated_quotes if q not in quotes]
    removals  = [q for q in quotes if q not in updated_quotes]
    for a in additions:
        logger.info(f"+ {' '.join(a)}")
    for r in removals:
        logger.info(f"- {' '.join(r)}")
    quotes = updated_quotes
