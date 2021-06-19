import datetime, time, discord, asyncio, random
from quotes import pull_random_quote

# Variables and stuff

client = discord.Client()
gnome = 356467595177885696
sandbox = 767326418572148756
colours = [0xc27c0e, 0x992d22, 0xad1457, 0x71368a, 0x206694, 0x11806a]
MINUTE = 60

# Quotes

with open("quotes.txt", "r") as file:
    quotes = [quote.split("###") for quote in file.read().splitlines()]

# Client events

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await client.change_presence(activity = discord.CustomActivity("Blah"))

@client.event
async def on_message(message):
    if message.author.id == gnome and message.channel.id == sandbox:
        if message.content == "#reroll":
            await send_quote("Re-rolled Quote")
    else: pass

@client.event
async def quote_loop():
    await client.wait_until_ready()
    while True:
        previous = datetime.datetime.now()
        await asyncio.sleep(MINUTE)
        now = datetime.datetime.now()
        if previous.hour != now.now().hour and now.hour == 12:
            await asyncio.sleep(15)
            await send_quote("Quote")

@client.event
async def send_quote(pre: str):
    quote = quotes[pull_random_quote()]
    embedVar = discord.Embed(title = "Maximum Swack!", description = quote[1], colour = random.choice(colours))
    embedVar.set_footer(text = f"{pre} for {datetime.datetime.now().strftime('%A %-d %B %Y')}\nSubmitted by {quote[0]}")
    await client.get_channel(sandbox).send(embed = embedVar)

# Run the thing

client.loop.create_task(quote_loop())
client.run(open("token.txt", "r").read())