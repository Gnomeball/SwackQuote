# SwackQuote

A repository for the QOTD bot on the **swack** Discord server.

To add a quote, [make an account](https://github.com/signup) on GitHub and [you can just edit the `quotes.toml` file in your browser](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files#editing-files-in-another-users-repository), and GitHub will walk you through the rest!

If you'd rather do it locally or step by step:
1. [fork this repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository)
2. [add the quote to `quotes.toml` (please read the formatting guide below)](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)
3. [update the trailing count comments](/README.md#formatting-for-quotes)
4. [make a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)

## Formatting for Quotes

All quotes are stored in `quotes.toml`, a flat-file following the [TOML specification](https://toml.io/en/). Quotes are formatted like so:

```toml
[identifier] # some unique, stable identifier, such as a date and number (2022-08-08-example-1)
submitter = "the name of who submitted it (aka, your discord handle/nickname)"
quote = "the quote you're adding"
attribution = "whoever said or wrote it, optionally where it was said or written"
source = "a URL for the quote or source, if you have it"
embed = false # true whenever the source should have an embed, such as a video
```

**You must include your name as the `submitter` and the `quote` itself, these are _required_.**

Currently, the `attribution`, `source`, and `embed` fields are optional, and default to empty/`false` when not set:
- If given, the `attribution` field will appear after the quote, separated by a `~`.
- If given, the `source` field will be linked to by the quote.
  - When `embed = true`, the `source` will be embedded beneath the quote (i.e. showing a YouTube video).

When adding quotes, **please** take care to update the trailing count comments, spaced out in groups of 5 quotes before a comment (so `#5` is followed by `#10` and so on). The one at the bottom should have the exact number of quotes, but if you round up to the nearest 5, then it's unlikely anyone will complain. **This is important!**

[All Discord-accepted markdown will be rendered properly](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101). Individual quotes **must** be less than 4000 bytes in size (encoded as UTF-8, total across all fields). In practice, we recommend quotes be less than 1500 bytes (UTF-8) anyway, as this would fill the screen on most mobile displays. Usually, a quote is much shorter anyway, just a couple of sentences at most. **When in doubt, keep it concise**, you can always link a `source` for those who want to see/hear more.

When required, attributions should follow the order: **`Author, Character, Work/Title, Edition/Episode, Year`**. These may be omitted where redundant or unknown (though we prefer an unknown author to be cited as such). Commas separate for clarity, and where clear may be removed or instead parenthesised.

Additional context or aspects of the attribution may be included if it is felt to improve the quote, preferably after the above ordering.

Due to the limitations of TOML and a desire for readability, we do not suggest or require quotation marks within the attribution; these are attributions, not citations, and it's easier for most people to just not worry about whether to use `"` or `'` and how to get that working within the TOML strings, so if you were to just write `attribution = "Terry Pratchet, The Colour of Magic"`, this would suffice.

When in doubt, ask someone, or look through the existing quotes for templates to follow!

### Quotes with unknown attribution

If you do not know who said/wrote the quote, or cannot find the original attribution, please use `Unknown` (or `Various` if likely disputed). If many have said it in one form or another, so there's no clear original/canonical form, use `Apocryphal`.

However, if you're having trouble finding the attribution, you can always ask others! They may know it themselves or know where to check (such as [Wikiquote](https://en.wikiquote.org/wiki/Main_Page) or your favourite search engine, these are particularly good at finding and dealing with misquotes or misattributions).

### Quotes from texts, books, shows, films, speeches, or other named works

If citing both a person and a work, please do this in a format that is sensible, perhaps `Person, Work`, inside the `attribution` field.

If the year or edition is relevant, include this either parenthesised `(3rd edition)` or following it `Unix Epoch, 1970`. With dating, we prefer and assume [Common Era](https://en.wikipedia.org/wiki/Common_Era), such as `Julius Caesar (100 - 44 BCE)` or `de Finibus Bonorum et Malorum, 45 BCE` (note that it is often implicit and omitted with modern dates).

Shows may include the specific episode by name and perhaps number, where relevant, but further details (such as timestamps) should not be included (but timestamped URLs for YouTube, say, may be used in the `source`).

Things like plays are often additionally attributed with `Act, Scene`, such as `William Shakespeare, Macbeth, Act V, Scene V`, however this is not a hard requirement.

### Quotes from fictional characters

Quotes taken from fiction should list the character.

When citing something said by a character, use a simple rule of thumb: if you know who wrote it, cite as `Author, Character`, otherwise cite the character directly.

For example, `The Doctor` or `Jean-Luc Picard` are cited as themselves because various scriptwriters and actors are involved, whereas Macbeth is cited as `William Shakespeare, Macbeth`, as we're quoting his script (the character should be listed, though it would be redundant in the case of Macbeth himself).

Other examples may be context-dependent, such as `Sherlock Holmes`, the books should be cited like `Arthur Conan Doyle, Sherlock Holmes, A Study in Scarlet`, whereas film or show adaptations may be cited like `Sherlock Holmes, Mr. Holmes` or `Sherlock Holmes, Sherlock` (according to `Character, Film/Show, Edition/Episode, Year`).

Redundancy is hard to judge in some cases, for example `The Doctor` is widely known for `Doctor Who`, but not everyone has seen it, so listing `The Doctor, Doctor Who` is not redundant, so unless the character's name is literally the name of the show/film/work, keep the title in (**in full**, so `Sherlock Holmes, Sherlock` isn't redundant). Just because some of us know it, doesn't mean all of us do.

While we appreciate the work of actors for characters (fictional or otherwise), they are generally not specific to the quotation as attribution usually goes to a creator via character (hence `Author, Character` ordering), though if the creator happens to be the actor (such as persona characters) then please follow `Author, Character` accordingly, as the actor is the author in these situations, for all intents and purposes. If you have evidence that a specific line was a particular person's creation, feel free to include that after the normal attribution (e.g. `Roy Batty, Blade Runner, ad-libbed by Rutger Hauer`).

Example:

```toml
[pre-toml-130]
submitter = "Gnome"
quote = "In the strict scientific sense we all feed on death - even vegetarians."
attribution = "Spock, Star Trek, Wolf in the Fold, stardate 3615.4"
```

### Quotes from antiquity

Quotes taken from antiquity should use [Common Era](https://en.wikipedia.org/wiki/Common_Era) dating, though this may be omitted outside uses of `BCE`, so dates like `1970` (implicit) and `400 BCE` (explicit) are the recommendation.

Once a date gets old enough that calendar changes become likely, please try to find the correct Common Era dating, though some antiquity calenders (such as various ancient Chinese calendars) might not have exact year-to-year matches (in which case, express it as a commonly agreed upon range in CE/BCE).

If a date is contested and given as a range, such as when a text was written, it is usually better to avoid including it, for concision. However, some texts are notably written over longer periods and are often given as a range, in which case this may be included if more significant than a later publishing date (such as accounts of protracted events).

Quotes specifically attributed to **someone** rather than to any of their given works may be given alongside the period in which they lived, as it is rare that more accurate dating is available, which would then follow as a range after their name, `Person, From–To` or `Person (From–To)`.

We recommend that date ranges use the `–` character to separate, as it is semantically the correct one, however this is not strictly enforced.

On the rare occasion it is available, more precise dating is usually not recommended (so no months or days), except when specifically relevant to the content of the quote (say about an astronomical event).

Example:

```toml
[2022-05-05-Yet-another-Greek-philosopher]
submitter = "Gnome"
quote = "There is nothing permanent except change."
attribution = "Heraclitus (535–475 BCE)"
```

### Quotes from someone with a long name

When citing someone, particularly with a long name or multiple middle names, please provide a reasonable version as they would have likely signed it, following an order like `<Title> <First Name> <Middle Initial>. <Middle Initial>. <Last Name>`, such as `Lord William T. Kelvin` or `W. E. B. de Bois`. Some names are to be given "in full" like `Arthur Conan Doyle`, based on popular recognition or stylisation, such as `Ian M. Banks` for quotes from that author's sci-fi writing, rather than `Ian Banks`, which would be used for quotes from his other writing.

Where possible, give whichever form of their name that person prefers most recently / at present, such as any stage name, online handle (such as `Kate @thingskatedid` for a Tweet), other pseudonyms/aliases, or simply whatever their preferred name is. **Do not deadname people.**

We ask that you do not unmask pseudonyms **except** where it is of a public figure that has already unveiled it **themselves**. For example, `Alice's Adventures in Wonderland` would be attributed to `Lewis Carroll`, not `Charles Dodgson`, as while Dodgson is the author, Carroll is the pen name attached to the publication of the book, as Dodgson never confirmed authorship in public. Beyond being decent, it is often simply not necessary to do so, as people can always look things up, after all.

### Quotes spanning multiple lines (such as code)

For quotes that span multiple lines, use `"""` at the beginning and end, on separate lines. The additional newlines introduced by this are ignored. If your quote contains `"`, you may wish to try using a `'raw string'`, which is also useful for quotes that contain inline code like `'print("hello, world")'`. If your quote contains both `"` and `'`, then a raw multi-line string can be used with `'''`, even on a single line (the TOML documentation recommends this approach).

For quotes containing blocks of code, use `'''` for raw multi-line strings, and then use ` ``` ` to create a code block, remembering to close them both afterwards. These should open together on the same line and close together on the same line, in the proper order. This may have syntax highlighting specified (might not work on all devices).

Example:

```toml
[2022-08-13-sudo]
submitter = "segfault"
quote = '''```bash
We trust you have received the usual lecture from the local System
Administrator.  It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.
```'''
attribution = "Todd C. Miller, `sudo`"
```

### Quotes with substitutions

Quotes where a word or phrase has been amended for clarity should surround that amendment in square brackets, such as `[We]`, while any omissions should use three periods for an ellipsis `...` either between fragments `"they would find ... just a single fruit"` or in place of the full stop ending a sentence `"Tell me... How many points did you get?"`. Any ellipsis used in the quote as typical punctuation (such as trailing off or extended pauses) is still accepted. Only if **both** a typical ellipsis and an omission would be present and ambiguous should you surround the omission with square brackets accordingly, like `[...]`.

There is no need to surround the starting letter of a quote if you capitalise it, even if it's starting mid-way through a sentence. Just capitalise it at the start as normal, so `"Hello, world!"` and `"Just a single fruit"` are correct, though specifically lower-case names or code should retain its original capitalisation (such as `"print(42)"`). We recommend that all other capitalisation in the quote remain unchanged (unless relevant or needed for clarity).

Example:

```toml
[2022-02-28-6]
submitter = "Gnome"
quote = "They journeyed a long time and found nothing.  At length they discerned a small light, which was the Earth...  [But] they could not find the smallest reason to suspect that we and our fellow-citizens of this globe have the honor to exist."
attribution = "Voltaire, Micromégas"
```

### Quotes with a valid URL

A single URL may be included in the `source` where relevant, i.e. for Tweets, videos, or articles (such as `source = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"`), and if `embed = true` is set for that quote, the URL will have an embed displayed alongside the quote. The embedding is janky, not visually appealing, and not what we desired; if you can improve this, please contribute!

Please only use `source` for HTTP/HTTPS URLs, so `source = "https://` and so on. We do not accept other URL formats at this time.

**Do not** put URLs in the `attribution`; Markdown links may be accepted, but lengthy raw URLs likely will not be, as they are often not very readable.

We recommend you **do not** set `embed = true` for most quotes that have a `source` URL, as the embed often duplicates the quote, adding visual clutter. A link to a video or audio recording is usually fine. This has great power, so use it wisely!

If `source` is a link to a video or audio, but it includes substantially more than the listed quote, we recommend you do not embed it, as the video/audio is not specifically of that quote (please no links to full episodes). This can be worked around when appropriately timestamped, such as with YouTube videos (ideally also working in the embed), in which case it may be accepted (again, no full episodes, please).

### Formatting Specification

Discord uses a dialect of Markdown, which we must encode in [TOML](https://toml.io/en/) accordingly, so when in doubt, RTFM:
- [The TOML documentation (for which string type to use, etc)](https://toml.io/en/)
- [The Discord Markdown documentation (for things like bold text, code, etc)](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101)

## Requirements to Build and Run

First and foremost, if you're wishing to run this bot on your own server, you must provide:
- [your own bot token](https://discordapp.com/developers/applications/) in `token.txt`
- [your user ID](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID) in `admins.toml` (with a nice handle in the format `<name> = <id>`, such as `gnome = 356467595177885696`)
- the [ID of the channel you](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID) wish the bot to use in `channel.txt`
- and, optionally, the [ID of your "lucky colour" role](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID) in `lucky_role.txt` (click on the `...` "More" in the Roles page).

**WARNING:** Your bot token must be kept private and secret; otherwise it can be hijacked! We have the `token.txt` file in the `.gitignore`, but please exercise caution!

Requirements:
- [py-cord](https://pypi.org/project/py-cord/)
- [tomli-w](https://pypi.org/project/tomli-w)
  - [python3-tomli-w](https://packages.debian.org/bookworm/python3-tomli-w)
- [requests](https://pypi.org/project/requests)
  - [python3-requests](https://packages.debian.org/bookworm/python3-requests)

We have a [poetry](https://python-poetry.org/) `pyproject.toml` setup for easy installation.  Just run `poetry update`!

## Inviting SwackQuote to your Server

Once you've set the bot up for yourself, you need to generate the OAuth2 URL for it, set to the `bot` scope. Our necessary bot permissions are `Read Messages/View Channels`, `Send Messages`, and `Embed Links`, so the OAuth2 URL should end with `&permissions=19456&scope=bot`. To use the Lucky Colour of the Day feature, we also need the `Manage Roles` permission, in which case the OAuth2 URL would end `&permissions=268454912&scope=bot`.

If you are using the Lucky Colour, you need a role setup for it. This role must be below the bot in the server's Roles settings, which if you are using it for messages, will unfortunately mean you have to put the bot's own role up quite high. Please make sure it's still beneath the role of your moderators, they need to be visible! This is a limitation of Discord's linear role hierarchy, but the code is small and clear enough that you can verify all we do is update the role's colour with this feature, and nothing else --- even sending a message about it is optional, just change `silent_update` to `True` when it's called.