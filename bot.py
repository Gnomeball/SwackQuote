import time, discord, asyncio, random, logging, sys
from datetime import datetime
from quotes import pull_random_quote, refresh_quotes

# Logging boilerplate
fmt = '[%(asctime)s: %(name)s %(levelname)s]: %(message)s'
logging.basicConfig(level = logging.WARNING, stream = sys.stdout, format = fmt)

# Variables and stuff
client = discord.Client()
logger = logging.getLogger("QuoteBot")

gnome = 356467595177885696
sandbox = 767326418572148756
colours = [0xc27c0e, 0x992d22, 0xad1457, 0x71368a, 0x206694, 0x11806a]

MINUTE = 60
REPO_LINK = "https://github.com/Gnomeball/QuoteBotRepo"

# Client events

@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")
    await client.change_presence(activity = discord.CustomActivity("Blah"))

@client.event
async def on_message(message):
    if message.channel.id == sandbox:
        if message.author.id == gnome:
            if message.content == "#reroll":
                await send_quote("Re-rolled Quote")
        if message.content == "#repo":
            await client.get_channel(sandbox).send(content = REPO_LINK)
    else: pass

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
    day_ord = "th" if 4 <= day_n % 100 <= 20 else {1:"st", 2:"nd", 3:"rd"}.get(day_n % 10, "th")
    return datetime.now().strftime('%A %-d# %B %Y').replace("#", day_ord)

@client.event
async def send_quote(pre = "Quote"):
    quotes = await refresh_quotes() # This way we have access to the latest quotes
    logger = logging.getLogger("send_quote")
    quote = pull_random_quote(quotes)
    quote_text = quote.quote
    if quote.attribution is not None: 
      quote_text += f" ~{quote.attribution}"
    embedVar = discord.Embed(title = "Maximum Swack!", description = quote_text, colour = random.choice(colours))
    embedVar.set_footer(text = f"{pre} for {current_date_time()}\nSubmitted by {quote.submitter}")
    logger.info(f"Sending quote from {quote.submitter}: {quote_text}")
    await client.get_channel(sandbox).send(embed = embedVar)

# Run the thing

client.loop.create_task(quote_loop())
client.run(open("token.txt", "r").read())
