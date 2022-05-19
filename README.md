# SwackQuote

A repository for the QOTD bot on the swan_hack Discord server.

To add a quote, fork, add it to `quotes.toml`, and make a pull request... hopefully it provides you less pain than it did me!

### Requirements

Requirements:
- discord.py
- tomli
- tomli-w

We have a [poetry](https://python-poetry.org/) `pyproject.toml` setup for easy installation.  Just run `poetry install`!

### Formatting for Quotes

The flat-file uses the TOML specification for storing quotes.  Quotes are formatted like so:

```toml
[identifier] # some stable identifier, such as a date
submitter = "the name of who submitted it (aka, your discord handle)"
quote = "the quote you're adding"
attribution = "whoever said or wrote it"
source = "where it was said or written, a url is nice if you have it (currently not displayed)"
```

**You must include your name as the `submitter`, and the `quote`, these are _required_.**

Currently, `attribution` and `source` are optional fields.

However, the `attribution` field will appear after the quote, behind a `~`, if given.

If you do not know who, or cannot find the original source, please use `unknown`, or `various`.

If citing both a person and a work, please do this in a format that is sensible, perhaps `person, work`, inside the `attribution` field - with anything more specific in the `source` field.

For quotes that span multiple lines, use `"""` at the beginning and end, on separate lines.

For quotes containing code, use `'''` for raw multi-line strings, and then use ` ``` ` to create a code block, remembering to close them both afterwards.

Any discord-accepted markdown should be parsed properly.

When adding quotes, please ensure to update the count.

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
