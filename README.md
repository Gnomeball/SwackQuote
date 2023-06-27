# SwackQuote

A repository for the QOTD bot on the swan_hack Discord server.

To add a quote, fork, add it to `quotes.toml`, and make a pull request... hopefully it provides you less pain than it did me!

## Requirements

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

## Formatting for Quotes

The flat-file uses the TOML specification for storing quotes.  Quotes are formatted like so:

```toml
[identifier] # some unique, stable identifier, such as a date and number (2022-08-08-example-1)
submitter = "the name of who submitted it (aka, your discord handle/nickname)"
quote = "the quote you're adding"
attribution = "whoever said or wrote it, optionally where it was said or written"
source = "a URL for the quote or source, if you have it"
embed = false # true whenever the source should have an embed, such as a video
```

**You must include your name as the `submitter`, and the `quote`, these are _required_.**

Currently, the `attribution`, `source`, and `embed` field are optional.

If given, the `attribution` field will appear after the quote, separated by a `~`. If given, the `source` field will be linked to by the quote. When `embed` is given as `embed = true` and a `source` has been provided, the source will be embedded beneath the quote (such as a YouTube video).

If you do not know who, or cannot find the original attribution, please use `Unknown`, or `Various`. If many have said it, use `Apocryphal`. But, if you're having trouble, you can always ask others who may know it themselves or know where to check (such as [Wikiquote](https://en.wikiquote.org/wiki/Main_Page) or your favourite search engine, these are particularly good at finding and dealing with misquotes or misattributions).

When citing someone, particularly with long middle names, please provide a reasonable version as they would have likely signed it, such as `<Title> <First Name> <Middle Initial>. <Middle Initial>. <Last Name>`, such as `Lord William T. Kelvin` or `W. E. B. de Bois`, though some names are to be given "in full" like `Arthur Conan Doyle`. Where possible give whichever form of their name that person prefers, including any stage name, online handle, other pseudonym/alias, or simply their preferred name. Do not deadname people. Do not unmask pseudonyms except where it is of a public figure that has already unveiled it (e.g. `Alice's Adventures in Wonderland` would be attributed to `Lewis Carroll`, not `Charles Dodgson`, as while Dodgson is the author, Lewis Carroll is the pen name attached to the publication of the book, and Dodgson never confirmed authorship in public). Beyond being decent, it is often simply not necessary to do so, as people can always look things up, after all.

If citing both a person and a work, please do this in a format that is sensible, perhaps `Person, Work`, inside the `attribution` field. Please only use `source` for HTTP/HTTPS URLs (where relevant, i.e. for Tweets, videos, or articles), and do not put URLs in the `attribution`, to keep it readable. If the year or edition is relevant, include this either parenthesised `(3rd edition)`, or following it like, say, `Unix Epoch, 1970`. With dating, we prefer and assume [Common Era](https://en.wikipedia.org/wiki/Common_Era), such as `Julius Caesar (100 - 44 BCE)` or `de Finibus Bonorum et Malorum, 45 BCE`.

When citing something said by a character, use a simple rule of thumb: if you know who wrote it, cite as `Author, Character`, otherwise cite the character directly. For example, `The Doctor` or `Jean-Luc Picard` are cited as themselves, because various scriptwriters and actors are involved, whereas Macbeth is cited as `William Shakespeare, Macbeth`, as we're quoting his script (the character should be listed, though it would be redundant in the case of Macbeth himself). Other examples may be context dependent, such as `Sherlock Holmes`, the books should be cited like `Arthur Conan Doyle, Sherlock Holmes, A Study in Scarlet`, whereas film or show adaptations may be cited  `Sherlock Holmes, Mr. Holmes` or `Sherlock Holmes, Sherlock` (according to `Character, Film/Show, Edition/Episode, Year`). Shows may include the specific episode by name and perhaps number, where relevant, but further details (timestamps etc.) should not be included (but timestamped URLs for YouTube, say, may be used in the `source`). Redundancy is hard to judge in some cases, for example `The Doctor` is widely known for `Doctor Who`, but not everyone has seen it, so listing `The Doctor, Doctor Who` is not redundant, so unless the character's name is literally the name of the show/movie (**in full**, so `Sherlock Holmes, Sherlock` isn't redundant), keep the title in. Just because some of us know it, doesn't mean all of us do.

So, when done properly, attributions should follow the order **`Author, Character, Work/Title, Edition/Episode, Year`**. These may be omitted where redundant or unknown (though we prefer an unknown author to be cited as such, except as in such cases as the examples above). Commas separate for clarity, and where clear may be removed or instead parenthesised (as in above examples). Additional context or aspects of the attribution may be included if it is felt to improve the quote, preferably after the above ordering. While we appreciate the work of actors of characters (fictional or otherwise), they are generally not specific to the quotation as attribution generally goes to a creator via character (hence `Author, Character` ordering), though if the creator happens to be the actor (such as persona characters) then please follow `Author, Character` accordingly. If you have evidence that a specific line was a particular person's creation, feel free to include that after the normal attribution (e.g. `Roy Batty, Blade Runner, ad-libbed by Rutger Hauer`).

Things like plays are often quoted with `Act, Scene`, such as `William Shakespeare, Macbeth, Act V, Scene V`, however this is not a hard requirement.

Do not put URLs in the attribution; Markdown links may be accepted, but lengthy raw URLs likely will not be. A single URL may be included in the `source` (i.e. `source = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"`), and if `embed = true` is set for that quote, the URL will have an embed displayed alongside the quote. The embedding is janky, not visually appealing, and not what we desired; if you can improve this, please contribute!

We do not recommend you set `embed` whenever you have a URL, as it may lead to duplication of the quote and visual clutter. Also, if it is a link to a video or audio, and it includes more than the listed quote, it should probably not be embedded, as the video/audio is not specifically a form of that quote.

For quotes that span multiple lines, use `"""` at the beginning and end, on separate lines. The additional newlines introduced by this are ignored. If your quote contains `"`, you may wish to try using a `'raw string'`, which are also useful for quotes that contain inline code like `'print("hello, world")'`. If your quote contains both `"` and `'`, then a raw multi-line string can be used with `'''`, even on a single line (the TOML documentation recommends this approach).

For quotes containing blocks of code, use `'''` for raw multi-line strings, and then use ` ``` ` to create a code block, remembering to close them both afterwards. These should open together on the same line and close together on the same line, in the proper order.

All Discord-accepted markdown should be rendered properly. Individual quotes must be less than 4000 bytes long (UTF-8, total across all fields). In practice, we recommend quotes be less than 1500 bytes (UTF-8), as with most character sets this would fill the screen on many mobile displays. Most of the time, they are much shorter anyway, just a couple sentences at most. When in doubt, keep it concise. You can always link a source for those who want to see/hear more.

When adding quotes, please take care to update the trailing count comments, spaced out in groups of 5 quotes before a comment (so `#5` is followed by `#10` and so on). The one at the bottom should have the exact number of quotes, but if you round up to the nearest 5 then it's unlikely anyone will complain.

### Quotes with substitutions

Quotes where a word or phrase has been amended for clarity should surround that amendment in square brackets, such as `[We]`, while any omissions should use three periods for an ellipsis `...` either between fragments `they would find ... just a single fruit` or in place of the full stop ending a sentence `Tell me... How many points did you get?`. Any ellipsis used in the quote as typical punctuation (trailing off, extended pauses, etc) is still accepted.

There is no need to made signify an amendment for the staring letter of a quote, even if it's starting mid-way through a sentence. You can just capitalise it as normal. We recommend that all other capitalisation in the quote remain unchanged (unless relevant or needed for clarity).

Example:

```toml
[2022-02-28-6]
submitter = "Gnome"
quote = "They journeyed a long time and found nothing.  At length they discerned a small light, which was the Earth...  [But] they could not find the smallest reason to suspect that we and our fellow-citizens of this globe have the honor to exist."
attribution = "Voltaire, Micromégas"
```

### Quotes from Fictional Characters

Quotes taken from fiction should list the character.

Example:

```toml
[pre-toml-130]
submitter = "Gnome"
quote = "In the strict scientific sense we all feed on death - even vegetarians."
attribution = "Spock, Star Trek, Wolf in the Fold, stardate 3615.4"
```

### Quotes from Antiquity

Quotes taken from antiquity should use [Common Era](https://en.wikipedia.org/wiki/Common_Era) dating.

Example:

```toml
[2022-05-05-Yet-another-Greek-philosopher]
submitter = "Gnome"
quote = "There is nothing permanent except change."
attribution = "Heraclitus (535–475 BCE)"
```

### Quotes from Code

Quotes of code should be multi-line strings starting with a code fence (not indentation based), which may have syntax highlighting specified (might not work on all devices). The multi-line string and code fence should start and end on the same line.

Example:

```toml
[pre-toml-300]
submitter = "Gnome"
quote = '''```python
def isprime(n): return not re.match(r"^1?$|^(11+?)\1+$", "1"*n)
```'''
attribution = "segfault"
```

### Formatting Specification

Discord uses a dialect of Markdown, which we must encode in TOML accordingly, so when in doubt, RTFM:
- [The TOML documentation for how strings work](https://toml.io/en/)
- [The Discord Markdown documentation for formatting](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101)
