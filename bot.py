import time, discord, asyncio, random, logging, sys
from datetime import datetime
from quotes import pull_random_quote, pull_quotes_from_repo, pull_quotes_from_file, refresh_quotes

# logging boilerplate
fmt = '[%(asctime)s: %(name)s %(levelname)s]: %(message)s'
logging.basicConfig(level = logging.INFO, stream = sys.stdout, format = fmt)

# Variables and stuff
client = discord.Client()
gnome = 356467595177885696
sandbox = 767326418572148756
logger = logging.getLogger("QuoteBot")
colours = [0xc27c0e, 0x992d22, 0xad1457, 0x71368a, 0x206694, 0x11806a]
MINUTE = 60

REPO_LINK = "https://github.com/Gnomeball/QuoteBotRepo"

# Quotes

quotes = pull_quotes_from_file()

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
async def send_quote(pre: str="Quote"):
    quotes = await refresh_quotes() # This way we have access to the latest quotes
    logger = logging.getLogger("send_quote")
    quote = pull_random_quote(quotes)
    embedVar = discord.Embed(title = "Maximum Swack!", description = quote[1], colour = random.choice(colours))
    embedVar.set_footer(text = f"{pre} for {datetime.now().strftime('%A %-d %B %Y')}\nSubmitted by {quote[0]}")
    logger.info(f"Sending quote: {quote}")
    await client.get_channel(sandbox).send(embed = embedVar)

# Run the thing

client.loop.create_task(quote_loop())
client.run(open("token.txt", "r").read())