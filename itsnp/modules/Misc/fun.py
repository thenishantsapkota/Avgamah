from datetime import datetime

import aiohttp
import hikari
import tanjun
from hikari import Embed

from itsnp.core.client import Client
from itsnp.utils.buttons import create_source_button
from itsnp.utils.pagination import paginate
from itsnp.utils.utilities import _chunk

component = tanjun.Component()


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command("cat", "Return a cat gif.", default_to_ephemeral=True)
async def cat_command(ctx: tanjun.abc.Context) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://some-random-api.ml/animal/cat") as resp:
            cat_json = await resp.json()

    embed = Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
        description=f"```{cat_json['fact']}```",
    )
    embed.set_author(name=f"Here's a cat for you!")
    embed.set_image(cat_json["image"])
    embed.set_footer(text=f"Requested by {ctx.author}")
    button = create_source_button(ctx, "https://some-random-api.ml/")

    await ctx.respond(embed=embed, component=button)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command("dog", "Return a dog gif.", default_to_ephemeral=True)
async def dog_command(ctx: tanjun.abc.Context) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://some-random-api.ml/animal/dog") as resp:
            dog_json = await resp.json()

    embed = Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
        description=f"```{dog_json['fact']}```",
    )
    embed.set_author(name=f"Here's a dog for you!")
    embed.set_image(dog_json["image"])
    embed.set_footer(text=f"Requested by {ctx.author}")
    button = create_source_button(ctx, "https://some-random-api.ml/")

    await ctx.respond(embed=embed, component=button)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("term", "Term to Search for")
@tanjun.as_slash_command("urban", "Search a term on urban dictionary")
async def urban_command(ctx: tanjun.abc.Context, term: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.urbandictionary.com/v0/define?term={term}"
        ) as resp:
            raw = await resp.json()

    urban_data = raw["list"]
    if not urban_data:
        return await ctx.respond("No Results :(")

    fields = (
        (
            hikari.UNDEFINED,
            hikari.Embed(
                title=f"Definition for {term}",
                description=f"{data[0]['definition']}\n\n**Example** - {data[0]['example']}\n**Link** - {data[0]['permalink']}",
                color=0x00FF00,
                timestamp=datetime.now().astimezone(),
            )
            .set_footer(f"Page {index+1}/{len(urban_data)}")
            .set_thumbnail(
                "https://images.squarespace-cdn.com/content/v1/586bd48d03596e5605450cee/1484851165621-U1SMXTW7C9X3BB3IEQ2U/image-asset.jpeg?format=1000w"
            ),
        )
        for index, data in enumerate(_chunk(urban_data, 1))
    )
    await paginate(ctx, fields, 180)


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
