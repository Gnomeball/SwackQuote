# QuoteBotRepo

A repository for the QOTD bot on the swan_hack Discord server.

To add a quote, fork, add it to `quotes.toml`, and make a pull request... hopefully it provides you less pain than it did me!

Requirements:
- discord.py
- tomli
- tomli-w

We have a [poetry](https://python-poetry.org/) `pyproject.toml` setup for easy installation. Just run `poetry install`!

Formatting:

```toml
[identifier] # some stable identifier, such as a date, and perhaps a number to prevent duplicates
submitter = "the name of who submitted it (aka, your discord handle/nickname)"
quote = "the quote you're adding!"
attribution = "whoever said it, if it wasn't the submitter (if you know, it's optional)"
source = "where it was said, a url is nice if you have it (optional, currently not displayed)"
```

**You must include your name as the `submitter` and the `quote`, these are _required_.**
Currently, `attribution` and `source` are optional fields.
If the quote spans multiple lines, use `"""` at the beginning and end.
If the quote contains code, use `'''` for raw multi-line strings, and then use ` ``` ` to create a code block.
Any discord-accepted markdown should be parsed properly.

For further reading, see:
- [The TOML documentation for how strings work](https://toml.io/en/)
- [The Discord Markdown documentation for formatting](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101)

Like so:

```toml
[2021-08-06-1]
submitter = "Gnome"
quote = "Hello, World!"
attribution = "Brian Kernighan"
```
