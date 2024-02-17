"""
A polite little Discord bot that can send out a quote each day.

`bot.py` focuses on the Discord integration only.
"""

import asyncio
import colorsys
import logging
import random
import re
import tomllib
from collections import Counter
from datetime import UTC, datetime
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import NoReturn

import discord

import logs
from quotes import (
    QUOTE_DECK_PATH,
    QUOTE_DUD_PATH,
    QUOTE_FILE_PATH,
    QUOTE_HISTORY_PATH,
    calculate_swack_level,
    format_quote_text,
    pull_random_quote,
    pull_specific_quote,
    refresh_quotes,
)

REPO_LINK = "https://github.com/Gnomeball/SwackQuote"
"Where is this repo, in case anybody asks?"

HELP_DOC = """Commands:
```js
#repo    - Prints out the URL for the GitHub repository
#authors - Prints a list of authors, with quote contribution counts
#help    - Prints out this message
```
Admin commands:
```js
#test <ID> - Sends a test quote, ID optional
#reroll    - Reroll todays quote
```
How to add a Quote:
```js
1. Go to the GitHub repository (#repo)
2. Fork the repository
3. Add your quote to quotes.toml (please read the formatting guide)
4. Update the comments with the current count
5. Open a pull request
Each step has a full guide and can be done in browser, no downloads required.
```
"""
"What SwackQuote can be asked to do."

RE_IS_URL = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", flags=re.I | re.M | re.U)
"Pattern to check if a string is most likely a URL. Credit to @stephenhay."

MINUTE = 60
"How long is a minute?"


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
    colour_hex = f"0x{''.join(hex(int(x * 255))[2:].zfill(2) for x in colour)}"
    return int(colour_hex, 16)


@client.event
async def on_ready() -> None:
    """SwackQuote has joined the server!"""
    logging.info(f"We have logged in as {client.user}")
    await client.change_presence(activity=discord.Game(name="Selecting a quote!"))


@client.event
async def on_message(message: discord.Message) -> None:
    """SwackQuote has been sent a message! Exciting!"""
    logger = logging.getLogger("on_message")
    if message.channel.id != CHANNEL:
        return
    match message.author.id, str.split(message.content):
        case user, ["#reroll", *_] if user in ADMINS:
            logger.info("Requesting quote re-roll")
            await send_quote("Re-rolled Quote", log="request_quote")
        case user, ["#test"] if user in ADMINS:
            logger.info("Requesting test quote")
            await test_quote()
        case user, ["#test", which, *_] if user in ADMINS:
            logger.info("Requesting test quote")
            await test_quote(which)
        case _, ["#repo", *_]:
            await client.get_channel(CHANNEL).send(content=REPO_LINK)
        case _, ["#authors", *_]:
            await author_counts()
        case _, ["#help", *_]:
            await send_help()


@client.event
async def send_help() -> None:
    """Prints out the help."""
    embed_msg = discord.Embed(title="Sending help!", colour=random_colour(), description=HELP_DOC)
    embed_msg.set_footer(text=f"Help for {await current_date_time()}")
    await client.get_channel(CHANNEL).send(embed=embed_msg)


@client.event
async def author_counts() -> None:
    """Who has contributed quotes (as self-assessed by the submitter field)."""
    quotes = await refresh_quotes()  # This way we have access to the latest quotes
    authors = dict(
        sorted(Counter(map(attrgetter("submitter"), quotes.values())).items(), key=itemgetter(1), reverse=True)
    )
    pad_name = max(map(len, authors)) + 1
    pad_num = max(map(len, map(str, authors.values()))) + 1

    # in py312 we can use f"{f"{a} ".ljust(pad_name, ".")}.{f" {authors[a]}".rjust(pad_num, ".")}"
    author_list = [".".join([f"{a} ".ljust(pad_name, "."), f" {authors[a]}".rjust(pad_num, ".")]) for a in authors]
    "Their name and number of submitted quotes, with our fun dot-based padding."
    author_string = "\n".join(["```", *author_list, "```"])
    "Formatted as a fenced block, so everything lines up nicely."

    embed_msg = discord.Embed(title="Submitters", colour=random_colour(), description=author_string)
    embed_msg.set_footer(text=f"Submitter table as of {await current_date_time()}")
    await client.get_channel(CHANNEL).send(embed=embed_msg)


@client.event
async def dud_quotes() -> None:
    """For when things go less than correct, try to let us know."""
    logger = logging.getLogger("dud_quotes")
    # We just print verbatim, no need to parse
    duds = Path(QUOTE_DUD_PATH).read_text().strip()
    if len(duds):
        logger.info(f"Sending dud quotes: \n{duds}")
        embed_msg = discord.Embed(
            title="These quotes need fixing", description=f"```toml\n{duds[:3900]}\n```", colour=random_colour()
        )
        await client.get_channel(CHANNEL).send(embed=embed_msg)
        logger.info("Dud quotes have been sent")
    else:
        logger.info("There were no dud quotes today")


@client.event
async def quote_loop() -> NoReturn:
    """Idles until we should start."""
    await client.wait_until_ready()
    logging.debug("Running quote loop")
    while True:
        previous = datetime.now(UTC)
        await asyncio.sleep(MINUTE)
        now = datetime.now(UTC)
        if previous.hour != now.now().hour and now.hour == 12:
            await asyncio.sleep(15)
            await send_quote()


@client.event
async def current_date_time() -> str:
    """Excuse me, could I bother you for the time?"""
    day_n = datetime.now(UTC).day
    day_ord = {1: "st", 2: "nd", 3: "rd", 7: "nth", 17: "nth", 21: "st", 22: "nd", 23: "rd", 27: "nth", 31: "st"}.get(
        day_n, "th"
    )
    return datetime.now(UTC).strftime("%A %-d# %B %Y").replace("#", day_ord)


@client.event
async def send_quote(
    pre: str = "Quote", title: str | None = None, which: str | None = None, log: str = "send_quote"
) -> None:
    """SwackQuote deployed. Quote inbound."""
    logger = logging.getLogger(log)

    quotes = await refresh_quotes()  # This way we have access to the latest quotes
    await dud_quotes()

    quote, i = pull_random_quote(quotes) if which is None else pull_specific_quote(which, quotes)
    title = title or calculate_swack_level()
    quote_text = format_quote_text(quote)

    # Build the quote embed we will send
    embed_msg = discord.Embed(title=title, colour=random_colour(), description=quote_text)
    embed_msg.set_footer(
        text=f"""{pre} for {await current_date_time()}
Quote {i}/{len(quotes)}, Submitted by {quote.submitter}"""
    )
    if quote.source and is_url(quote.source):
        embed_msg.url = quote.source
        embed_msg.title += " 🔗"

    # Try and send the quote
    logger.info(f"Attempting to send quote #{i}, submitted by {quote.submitter}")
    try:
        await client.get_channel(CHANNEL).send(embed=embed_msg)
        if quote.embed and quote.source and is_url(quote.source):
            await client.get_channel(CHANNEL).send(content=quote.source)
    except Exception:
        logger.exception(f"Error sending quote #{i}")
    finally:
        logger.info("Quote sent successfully")


@client.event
async def test_quote(which: str = "pre-toml-255", log: str = "test_quote") -> None:
    """Send our default testing quote, or another one of your choice, marked up so we can tell."""
    await send_quote(pre="Testing", title="Testing the Swack", which=which, log=log)


if __name__ == "__main__":
    # Variables and stuff
    intents = discord.Intents.default()
    intents.message_content = True

    # Prepare the client and logging
    logs.init()
    client = discord.Client(intents=intents)
    logger = logging.getLogger("SwackQuote")

    # Permissions and directions for SwackQuote
    ADMINS = set(tomllib.loads(Path("admins.toml").read_text()).values())
    "Those able to send commands to Swackquote."
    CHANNEL = int(Path("channel.txt").read_text())
    "Which channel SwackQuote will move to, place quotes in, and monitor for commands."

    # Ensure necessary files exist
    QUOTE_FILE_PATH.touch()
    QUOTE_DUD_PATH.touch()
    QUOTE_DECK_PATH.touch()
    QUOTE_HISTORY_PATH.touch()

    client.loop.create_task(quote_loop())
    client.run(Path("token.txt").read_text())
