# SwackQuote

A repository for the QOTD bot on the swan_hack Discord server.

To add a quote, fork, add it to `quotes.toml`, and make a pull request... hopefully it provides you less pain than it did me!

### Requirements

First and foremost, if you're wishing to run this bot on your own server, you must provide:
- [your own bot token](https://discordapp.com/developers/applications/) in `token.txt`
- [your user ID](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) in `admins.toml` (with a nice handle in the format `<name> = <id>`, such as `gnome = 356467595177885696`)
- the [ID of the channel you](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) wish the bot to use in `channel.txt`.

Requirements:
- [py-cord](https://pypi.org/project/py-cord/)
- [tomli](https://pypi.org/project/tomli)
- [tomli-w](https://pypi.org/project/tomli-w)
- [requests](https://pypi.org/project/requests)

We have a [poetry](https://python-poetry.org/) `pyproject.toml` setup for easy installation.  Just run `poetry install`!

### Formatting for Quotes

The flat-file uses the TOML specification for storing quotes.  Quotes are formatted like so:

```toml
[identifier] # some unique, stable identifier, such as a date and number (2022-08-08-example-1)
submitter = "the name of who submitted it (aka, your discord handle)"
quote = "the quote you're adding"
attribution = "whoever said or wrote it"
source = "where it was said or written, a url is nice if you have it (currently not displayed)"
```

**You must include your name as the `submitter`, and the `quote`, these are _required_.**

Currently, `attribution` and `source` are optional fields.

However, the `attribution` field will appear after the quote, behind a `~`, if given.

If you do not know who, or cannot find the original attribution, please use `Unknown`, or `Various`. If many have said it, use `Apocryphal`. But, if you're having trouble, you can always ask others, who may know it themselves or know where to check.

If citing both a person and a work, please do this in a format that is sensible, perhaps `person, work`, inside the `attribution` field --- with anything more specific (i.e. URLs for Tweets) in the `source` field.

For quotes that span multiple lines, use `"""` at the beginning and end, on separate lines.

For quotes containing code, use `'''` for raw multi-line strings, and then use ` ``` ` to create a code block, remembering to close them both afterwards.

All discord-accepted markdown should be parsed properly. Individual quotes must be less than 4000 bytes long (UTF-8).

When adding quotes, please take care to update the trailing count comments, spaced out in groups of 5 quotes before a comment (so `#5` if followed by `#10` and so on). The one at the bottom should have the exact number of quotes, but if you round up to the nearest 5 then it's unlikely anyone will complain.

### Quotes from Fictional Characters

Quotes taken from fiction should list the character.

Example:

```toml
[pre-toml-130]
submitter = "Gnome"
quote = "In the strict scientific sense we all feed on death - even vegetarians."
attribution = "Spock, Wolf in the Fold, stardate 3615.4"
```

### Quotes from Antiquity

Quotes taken from antiquity should use [Common Era](https://en.wikipedia.org/wiki/Common_Era) dating.

Example:

```toml
[2022-05-05-Yet-another-Greek-philosopher]
submitter = "Gnome"
quote = "There is nothing permanent except change."
attribution = "Heraclitus (535-475 BCE)"
```

### Further Reading

For further reading, see:
- [The TOML documentation for how strings work](https://toml.io/en/)
- [The Discord Markdown documentation for formatting](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101)
