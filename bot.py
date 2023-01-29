from operator import attrgetter
from operator import itemgetter
from collections import Counter
from datetime import datetime
from typing import Optional
from pathlib import Path
import colorsys
import logging
import asyncio
import random
import re

import discord
import tomli
import logs

from quotes import (
    calculate_swack_level,
    pull_specific_quote,
    pull_random_quote,
    format_quote_text,
    refresh_quotes,
    QUOTE_HISTORY_PATH,
    QUOTE_FILE_PATH,
    QUOTE_DECK_PATH,
    QUOTE_DUD_PATH,
)

# Variables and stuff
intents = discord.Intents.default()
intents.message_content = True

# Prepare the client and logging
logs.init()
client = discord.Client(intents = intents)
logger = logging.getLogger("QuoteBot")

# Those able to send commands to the bot and which channel it must be in
ADMINS  = set(tomli.loads(Path("admins.toml").read_text()).values())
CHANNEL = int(Path("channel.txt").read_text())

MINUTE = 60
REPO_LINK = "https://github.com/Gnomeball/SwackQuote"

# regex is by @stephenhay
RE_IS_URL = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", flags = re.I | re.M | re.U)

# Auxiliary functions

def is_url(url: str) -> bool:
  """
  Check if a string is a valid URL for Discord.
  Some invalid URLs may get through, but all valid URLs will pass.
  Things that are absolutely not URLs will fail.
  :returns: whether the given string is a valid URL.
  :rtype: bool
  """
  return re.match(RE_IS_URL, url) is not None

def random_colour() -> int:
    """
    Calculates a random (ish) Hex colour - Used to make embeds a little less boring.
    :returns: integer value for a colour.
    :rtype: int
    """
    colour = colorsys.hsv_to_rgb(random.random(), random.uniform(0.42, 0.98), random.uniform(0.4, 0.9))
    colour_hex = "0x" + "".join(hex(int(x*255))[2:].zfill(2) for x in colour)
    return int(colour_hex, 16)

# Client events

@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")
    await client.change_presence(activity = discord.Game(name = "Selecting a quote!"))

@client.event
async def on_message(message: discord.Message):
    logger = logging.getLogger("on_message")
    if message.channel.id == CHANNEL:
        if message.author.id in ADMINS:
            if message.content == "#reroll":
                logger.info("Requesting quote re-roll")
                await send_quote("Re-rolled Quote", log = "quote_request")
            if message.content[:5] == "#test":
                logger.info("Requesting test quote")
                await test_quote(message.content[5:].strip(), log = "quote_request")
        if message.content == "#repo":
            await client.get_channel(CHANNEL).send(content = REPO_LINK)
        if message.content == "#authors":
            await author_counts()
        if message.content == "#help":
            await send_help()
    else:
        pass

@client.event
async def send_help():
    """
    Prints out the help
    """
    help_string = """Commands:
```
Usable by owner only:

#test <ID> - Sends a test quote, ID optional
#reroll    - Reroll todays quote

Usable by anyone:

#repo    - Prints out the URL for the GitHub repository
#authors - Prints a list of authors, with quote contribution counts
#help    - Prints out this message
```
How to add a Quote:
```
1. Go to the GitHub repository
2. Fork the repository to create a remote copy
3. Clone and pull this copy to your local machine
4. Add your quote(s) to quotes.toml (be sure to update the count)
5. Commit and push to your own remote repository
6. Open a pull request to the main GitHub repository
```
"""
    embedVar = discord.Embed(title = "Sending help!", colour = random_colour(), description = help_string)
    embedVar.set_footer(text = f"Help for {await current_date_time()}")
    await client.get_channel(CHANNEL).send(embed = embedVar)

@client.event
async def author_counts():
    quotes = await refresh_quotes() # This way we have access to the latest quotes
    authors = dict(sorted(Counter(map(attrgetter("submitter"), quotes.values())).items(), key = itemgetter(1), reverse = True))
    pad = max(len(a) for a in authors)

    author_string = "```\n"
    for a in authors: # Name, padded with a space and dots, a dot, then, padded with dots and a space, their count
        author_string += f"{a + ' '.ljust(pad + 1 - len(a), '.')}.{' '.rjust(4 - len(str(authors[a])), '.') + str(authors[a])}\n"
    author_string += "```"

    embedVar = discord.Embed(title = "Submitters", colour = random_colour(), description = author_string)
    embedVar.set_footer(text = f"Submitter table as of {await current_date_time()}")
    await client.get_channel(CHANNEL).send(embed = embedVar)

@client.event
async def dud_quotes():
    logger = logging.getLogger("dud_quotes")
    # We just print verbatim, no need to parse
    duds = Path(QUOTE_DUD_PATH).read_text().strip()
    if len(duds):
        logger.info(f"Sending dud quotes: \n{duds}")
        embedVar = discord.Embed(title = "These quotes need fixing", description = f"```toml\n{duds[:4000]}\n```", colour = random_colour())
        await client.get_channel(CHANNEL).send(embed = embedVar)
        logger.info("Dud quotes have been sent")
    else:
        logger.info("There were no dud quotes today")

@client.event
async def quote_loop():
    await client.wait_until_ready()
    logging.debug(f"Running quote loop @ {datetime.now()}")
    while True:
        previous = datetime.now()
        await asyncio.sleep(MINUTE)
        now = datetime.now()
        if previous.hour != now.now().hour and now.hour == 12:
            await asyncio.sleep(15)
            await send_quote()

@client.event
async def current_date_time():
    day_n = datetime.now().day
    day_ord = { 1: "st",  2: "nd",  3: "rd",  7: "nth", 17: "nth",
               21: "st", 22: "nd", 23: "rd", 27: "nth", 31: "st"}.get(day_n, "th")
    return datetime.now().strftime("%A %-d# %B %Y").replace("#", day_ord)

@client.event
async def send_quote(pre: str = "Quote", title: Optional[str] = None, which: Optional[str] = None, log: str = "send_quote"):
    logger = logging.getLogger(log)

    quotes = await refresh_quotes() # This way we have access to the latest quotes
    await dud_quotes()

    quote, i = pull_random_quote(quotes) if which is None else pull_specific_quote(which, quotes)
    title = calculate_swack_level() if title is None else title

    quote_text = format_quote_text(quote)

    # Build the quote embed
    embedVar = discord.Embed(title = title, colour = random_colour(), description = quote_text)
    if quote.source and is_url(quote.source):
        embedVar.url = quote.source
    embedVar.set_footer(text = f"{pre} for {await current_date_time()}\nQuote {i}/{len(quotes)}, Submitted by {quote.submitter}")

    # Try and send the quote
    logger.info(f"Attempting to send quote #{i}, submitted by {quote.submitter}")
    try:
        await client.get_channel(CHANNEL).send(embed = embedVar)
        if quote.embed and quote.source and is_url(quote.source):
            await client.get_channel(CHANNEL).send(content = quote.source)
    except Exception:
        logger.exception(f"Error sending quote #{i}")
    finally:
        logger.info("Quote sent successfully")

@client.event
async def test_quote(which = "pre-toml-255", log: str = "test_quote"):
    await send_quote(pre = "Testing", title = "Testing the Swack", which = which, log = log)

# Run the thing

QUOTE_FILE_PATH.touch()
QUOTE_DUD_PATH.touch()
QUOTE_DECK_PATH.touch()
QUOTE_HISTORY_PATH.touch()

client.loop.create_task(quote_loop())
client.run(Path("token.txt").read_text())
