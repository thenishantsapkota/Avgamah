import asyncio
import typing as t
from datetime import datetime

import hikari
import tanjun
from hikari import Embed

from itsnp.core.client import Client
from models import TagModel

component = tanjun.Component()

tag_group = tanjun.slash_command_group("tag", "Tag slash command group")


@tag_group.with_command
@tanjun.with_str_slash_option("value", "Value of the tag.")
@tanjun.with_str_slash_option("name", "Name of the tag you want to store.")
@tanjun.as_slash_command("add", "Add a tag to the database.")
async def add_tag_command(ctx: tanjun.abc.Context, name: str, *, value: str) -> None:
    model, _ = await TagModel.get_or_create(guild_id=ctx.guild_id, name_tag=name)
    model.name_tag = name
    model.tag_value = value
    await model.save()
    embed = Embed(
        description=value,
        color=hikari.Color(0xF1C40F),
        timestamp=datetime.now().astimezone(),
    )
    embed.set_author(name=f"Name: {name}", icon=ctx.author.avatar_url)
    embed.set_footer(text=f"Tag created by {ctx.author}")
    await ctx.respond(embed=embed)


@tag_group.with_command
@tanjun.with_str_slash_option(
    "name", "Name of the tag you want to display", default=None
)
@tanjun.as_slash_command("show", "Get the info about the tag")
async def display_tag_command(ctx: tanjun.abc.Context, name: t.Optional[str]) -> None:
    if name:
        model = await TagModel.get_or_none(name_tag=name.lower())
        if model is None:
            return await ctx.respond("Tag doesn't exist.")
        await ctx.respond(model.tag_value)
        return

    tags = await TagModel.filter(guild_id=ctx.guild_id)
    all_tags = "\n".join(
        [f"**{i+1}.**  {model.name_tag}" for (i, model) in enumerate(tags)]
    )
    embed = Embed(
        title="List of all Tags",
        description=all_tags if len(all_tags) else "No Tags.",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0xF1C40F),
    )

    embed.set_footer(text=f"Invoked by {ctx.author}")
    await ctx.respond(embed=embed)


@tag_group.with_command
@tanjun.with_str_slash_option("name", "Name of the tag.")
@tanjun.as_slash_command("delete", "Delete a tag")
async def delete_tag(ctx: tanjun.abc.Context, name: str) -> None:
    model = await TagModel.get_or_none(name_tag=name, guild_id=ctx.guild_id)
    await model.delete()
    await ctx.respond("Tag deleted successfully!")


component.add_slash_command(tag_group)


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
