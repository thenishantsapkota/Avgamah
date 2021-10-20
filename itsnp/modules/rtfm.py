import warnings
from datetime import datetime

import aiohttp
import hikari
import tanjun
from hikari import Embed
from tanjun.clients import as_loader

from itsnp.core.client import Client
from itsnp.utils.buttons import create_source_button
from itsnp.utils.fuzzy import *
from itsnp.utils.pagination import paginate
from itsnp.utils.rtfm import *
from itsnp.utils.utilities import _chunk

component = tanjun.Component()

TARGETS = {
    "python": "https://docs.python.org/3",
    "discord.py": "https://discordpy.readthedocs.io/en/latest",
    "numpy": "https://numpy.readthedocs.io/en/latest",
    "pandas": "https://pandas.pydata.org/docs",
    "pillow": "https://pillow.readthedocs.io/en/stable",
    "imageio": "https://imageio.readthedocs.io/en/stable",
    "requests": "https://requests.readthedocs.io/en/master",
    "aiohttp": "https://docs.aiohttp.org/en/stable",
    "django": "https://django.readthedocs.io/en/stable",
    "flask": "https://flask.palletsprojects.com/en/1.1.x",
    "praw": "https://praw.readthedocs.io/en/latest",
    "apraw": "https://apraw.readthedocs.io/en/latest",
    "asyncpg": "https://magicstack.github.io/asyncpg/current",
    "aiosqlite": "https://aiosqlite.omnilib.dev/en/latest",
    "sqlalchemy": "https://docs.sqlalchemy.org/en/14",
    "tensorflow": "https://www.tensorflow.org/api_docs/python",
    "matplotlib": "https://matplotlib.org/stable",
    "seaborn": "https://seaborn.pydata.org",
    "pygame": "https://www.pygame.org/docs",
    "simplejson": "https://simplejson.readthedocs.io/en/latest",
    "wikipedia": "https://wikipedia.readthedocs.io/en/latest",
    "hikari": "https://hikari-py.github.io/hikari/",
    "lightbulb": "https://hikari-lightbulb.readthedocs.io/en/latest/",
    "nepse-api": "https://nepse-api.readthedocs.io/en/latest/",
}

ALIASES = {
    ("py", "py3", "python3", "python"): "python",
    ("dpy", "discord.py", "discordpy"): "discord.py",
    ("np", "numpy", "num"): "numpy",
    ("pd", "pandas", "panda"): "pandas",
    ("pillow", "pil"): "pillow",
    ("imageio", "imgio", "img"): "imageio",
    ("requests", "req"): "requests",
    ("aiohttp", "http"): "aiohttp",
    ("django", "dj"): "django",
    ("flask", "fl"): "flask",
    ("reddit", "praw", "pr"): "praw",
    ("asyncpraw", "apraw", "apr"): "apraw",
    ("asyncpg", "pg"): "asyncpg",
    ("aiosqlite", "sqlite", "sqlite3", "sqli"): "aiosqlite",
    ("sqlalchemy", "sql", "alchemy", "alchem"): "sqlalchemy",
    ("tensorflow", "tf"): "tensorflow",
    ("matplotlib", "mpl", "plt"): "matplotlib",
    ("seaborn", "sea"): "seaborn",
    ("pygame", "pyg", "game"): "pygame",
    ("simplejson", "sjson", "json"): "simplejson",
    ("wiki", "wikipedia"): "wikipedia",
    ("hikari", "bhikari"): "hikari",
    ("lightbulb", "batti"): "lightbulb",
    ("nepse-api", "samrid"): "nepse-api",
}

MODULES = list(TARGETS.keys())

URL_OVERRIDES = {
    "tensorflow": "https://github.com/mr-ubik/tensorflow-intersphinx/raw/master/tf2_py_objects.inv"
}

cache = {}


async def build(target) -> None:
    url = TARGETS[target]
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_OVERRIDES.get(target, url + "/objects.inv")) as resp:
            if resp.status != 200:
                warnings.warn(
                    Warning(
                        f"Received response with status code {resp.status} when trying to build RTFM cache for {target} through {url}/objects.inv"
                    )
                )
                raise tanjun.CommandError("Failed to build RTFM cache")
            cache[target] = SphinxObjectFileReader(await resp.read()).parse_object_inv(
                url
            )


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.READ_MESSAGE_HISTORY
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("term", "Term to search for")
@tanjun.with_str_slash_option(
    "doc", "Documentation of Library", choices=(l.lower() for l in TARGETS.keys())
)
@tanjun.as_slash_command("rtfm", "Search through docs of a module/python")
async def rtfm_command(ctx: tanjun.abc.Context, doc: str, *, term: str) -> None:
    global cache
    doc = doc.lower()
    target = None
    for aliases, target_name in ALIASES.items():
        if doc in aliases:
            target = target_name

    caches = cache.get(target)
    if not caches:
        await build(target)
        caches = cache.get(target)

    results = finder(term, list(caches.items()), key=lambda x: x[0], lazy=False)[:20]

    if not results:
        return await ctx.respond("Couldn't find any results")
    fields = (
        (
            hikari.UNDEFINED,
            hikari.Embed(
                title=f"Searched in {target}",
                description="\n".join([f"[`{key}`]({url})" for key, url in result]),
                color=0x00FF00,
                timestamp=datetime.now().astimezone(),
            ).set_footer(f"Page {index+1}"),
        )
        for index, result in enumerate(_chunk(results, 5))
    )

    await paginate(ctx, fields, 180)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.READ_MESSAGE_HISTORY
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command(
    "rtfmlist", "List all the avaliable documentation search targets"
)
async def rtfmlist_command(ctx: tanjun.abc.Context) -> None:
    aliases = {v: k for k, v in ALIASES.items()}
    embed = hikari.Embed(title="RTFM list of avaliable modules", color=0xF1C40F)
    embed.description = "\n".join(
        [
            "[{0}]({1}): {2}".format(
                target,
                link,
                "\u2800".join([f"`{i}`" for i in aliases[target] if i != target]),
            )
            for target, link in TARGETS.items()
        ]
    )

    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
