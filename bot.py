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

# Random colours for the embed

def random_colour_hex():
    colour = colorsys.hsv_to_rgb(random.random(), random.uniform(0.42, 0.98), random.uniform(0.4, 0.9))
    return "0x" + "".join(hex(int(x*255))[2:].zfill(2) for x in colour)

def random_colour():
    return int(random_colour_hex(), 16)

# Client events

@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")
    # await client.change_presence(activity = discord.CustomActivity("Blah"))
    await client.change_presence(activity = discord.Game(name = "Selecting a quote!"))

@client.event
async def on_message(message: discord.Message):
    if message.channel.id == CHANNEL:
        if message.author.id in ADMINS:
            if message.content == "#reroll":
                await send_quote("Re-rolled Quote")
            if message.content[:5] == "#test":
                await test_quote(message.content[5:].strip())
        if message.content == "#repo":
            await client.get_channel(CHANNEL).send(content = REPO_LINK)
    else: pass

@client.event
async def dud_quotes():
    logger = logging.getLogger("dud_quotes")
    Path(QUOTE_DUD_PATH).touch()
    duds = Path(QUOTE_DUD_PATH).read_text().strip() # we just print verbatim, no need to parse
    if len(duds):
        logger.info(f"Sending dud quotes: \n{duds}")
        embedVar = discord.Embed(title = "These quotes need fixing", description = f"```\n{duds[:4000]}\n```", colour = random_colour())
        await client.get_channel(CHANNEL).send(embed = embedVar)
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
    quotes = await refresh_quotes() # This way we have access to the latest quotes
    logger = logging.getLogger(log)
    await dud_quotes()
    quote, i = pull_random_quote(quotes) if which is None else pull_specific_quote(which, quotes)
    quote_text = format_quote_text(quote)
    title = calculate_swack_level() if title is None else title
    embedVar = discord.Embed(title = title, description = quote_text, colour = random_colour())
    embedVar.set_footer(text = f"{pre} for {await current_date_time()}\nQuote {i}/{len(quotes)}, Submitted by {quote.submitter}")
    logger.info(f"Sending quote from {quote.submitter}: {quote_text}")
    await client.get_channel(CHANNEL).send(embed = embedVar)

@client.event
async def test_quote(which = "pre-toml-255"):
    await send_quote(pre = "Testing", title = "Testing the Swack", which = which, log = "test_quote")

# Run the thing

QUOTE_FILE_PATH.touch()
QUOTE_DUD_PATH.touch()
QUOTE_DECK_PATH.touch()
QUOTE_HISTORY_PATH.touch()

client.loop.create_task(quote_loop())
client.run(Path("token.txt").read_text())
