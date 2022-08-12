import time, discord, asyncio, random, logging, sys, colorsys
from datetime import datetime
from quotes import pull_random_quote, pull_specific_quote, refresh_quotes, format_quote_text, calculate_swack_level

# Logging boilerplate
fmt = '[%(asctime)s: %(name)s %(levelname)s]: %(message)s'
logging.basicConfig(level = logging.INFO, stream = sys.stdout, format = fmt)

# Variables and stuff
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
logger = logging.getLogger("QuoteBot")

gnome   = 356467595177885696
sandbox = 767326418572148756
# colours = [0xc27c0e, 0x992d22, 0xad1457, 0x71368a, 0x206694, 0x11806a]

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
async def on_message(message):
    if message.channel.id == sandbox:
        if message.author.id == gnome:
            if message.content == "#reroll":
                await send_quote("Re-rolled Quote")
            if message.content[:5] == "#test":
                await test_quote(message.content[5:].strip())
        if message.content == "#repo":
            await client.get_channel(sandbox).send(content = REPO_LINK)
    else: pass

@client.event
async def quote_warning(logger):
  # TODO: pull latest duds from quote_duds.toml and let us know. A message with the identifier is the MVP.
  pass

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
    day_ord = {1:"st", 21:"st", 31:"st", 2:"nd", 22:"nd", 3:"rd", 23:"rd", 7:"nth", 17:"nth", 27:"nth"}.get(day_n, "th")
    return datetime.now().strftime('%A %-d# %B %Y').replace("#", day_ord)

@client.event
async def send_quote(pre = "Quote"):
    quotes = await refresh_quotes() # This way we have access to the latest quotes
    logger = logging.getLogger("send_quote")
    quote_warning(logger)
    quote, quote_index = pull_random_quote(quotes)
    quote_text = format_quote_text(quote)
    swack_level = calculate_swack_level()
    embedVar = discord.Embed(title = swack_level, description = quote_text, colour = random_colour())
    embedVar.set_footer(text = f"{pre} for {await current_date_time()}\nQuote {quote_index}/{len(quotes)}, Submitted by {quote.submitter}")
    logger.info(f"Sending quote from {quote.submitter}: {quote_text}")
    await client.get_channel(sandbox).send(embed = embedVar)

@client.event
async def test_quote(which = "pre-toml-255"):
    quotes = await refresh_quotes() # This way we have access to the latest quotes
    logger = logging.getLogger("test_quote")
    quote_warning(logger)
    quote, quote_index = pull_specific_quote(which, quotes)
    quote_text = format_quote_text(quote)
    embedVar = discord.Embed(title = "Testing the Swack", description = quote_text, colour = random_colour())
    embedVar.set_footer(text = f"Test for {await current_date_time()}\nQuote {quote_index}/{len(quotes)}, Submitted by {quote.submitter}")
    logger.info(f"Sending quote from {quote.submitter}: {quote_text}")
    await client.get_channel(sandbox).send(embed = embedVar)

# Run the thing

client.loop.create_task(quote_loop())
client.run(open("token.txt", "r").read())
