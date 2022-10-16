import discord, asyncio, random, logging, sys, colorsys
from datetime import datetime
from typing import Optional
from pathlib import Path

import tomli

from quotes import pull_random_quote, pull_specific_quote, refresh_quotes, format_quote_text, calculate_swack_level, QUOTE_FILE_PATH, QUOTE_DUD_PATH, QUOTE_DECK_PATH, QUOTE_HISTORY_PATH

# Logging boilerplate
fmt = "[%(asctime)s: %(name)s %(levelname)s]: %(message)s"
logging.basicConfig(level = logging.INFO, stream = sys.stdout, format = fmt)

# Variables and stuff
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents = intents)
logger = logging.getLogger("QuoteBot")

# Those able to send commands to the bot and which channel it must be in
ADMINS  = set(tomli.loads(Path("admins.toml").read_text()).values())
CHANNEL = int(Path("channel.txt").read_text())

MINUTE = 60
REPO_LINK = "https://github.com/Gnomeball/SwackQuote"

# Auxiliary functions

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
                logger.info(f"Requesting quote re-roll")
                await send_quote("Re-rolled Quote", log="quote_request")
            if message.content[:5] == "#test":
                logger.info(f"Requesting test quote")
                await test_quote(message.content[5:].strip(), log="quote_request")
        if message.content == "#repo":
            await client.get_channel(CHANNEL).send(content = REPO_LINK)
    else:
        pass

@client.event
async def dud_quotes():
    logger = logging.getLogger("dud_quotes")
    # * We just print verbatim, no need to parse
    duds = Path(QUOTE_DUD_PATH).read_text().strip()
    if len(duds):
        logger.info(f"Sending dud quotes: \n{duds}")
        embedVar = discord.Embed(title = "These quotes need fixing", description = f"```toml\n{duds[:4000]}\n```", colour = random_colour())
        await client.get_channel(CHANNEL).send(embed = embedVar)
        logger.info(f"Dud quotes have been sent")
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
    day_ord = {1: "st", 21: "st", 31: "st", 2: "nd", 22: "nd", 3: "rd", 23: "rd", 7: "nth", 17: "nth", 27: "nth"}.get(day_n, "th")
    return datetime.now().strftime("%A %-d# %B %Y").replace("#", day_ord)

@client.event
async def send_quote(pre: str = "Quote", title: Optional[str] = None, which: Optional[str] = None, log: str = "send_quote"):
    logger = logging.getLogger(log)

    quotes = await refresh_quotes() # This way we have access to the latest quotes
    await dud_quotes()

    quote, i = pull_random_quote(quotes) if which is None else pull_specific_quote(which, quotes)
    quote_text = format_quote_text(quote)
    title = calculate_swack_level() if title is None else title

    # TODO: better check for if its a url
    quoteIsUrl = quote.quote == quote.source and quote.source.startswith("http")

    # Build the quote embed
    embedVar = discord.Embed( title = title, colour = random_colour(), description = "" if quoteIsUrl else quote_text)
    # TODO: again, better url check
    if quote.source and quote.source.startswith("http"):
        embedVar.url = quote.source
    embedVar.set_footer(text = f"{pre} for {await current_date_time()}\nQuote {i}/{len(quotes)}, Submitted by {quote.submitter}")

    # Try and send the quote
    logger.info(f"Attempting to send quote #{i}, submitted by {quote.submitter}")
    try:
        await client.get_channel(CHANNEL).send(embed = embedVar)
        if quoteIsUrl:
            await client.get_channel(CHANNEL).send(content = quote.source)
    except Exception as e:
        logger.info(f"Error sending quote : {e}")
    finally:
        logger.info(f"Quote sent successfully")

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
