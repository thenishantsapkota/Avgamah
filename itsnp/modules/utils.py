import io

import aiohttp
import hikari
import tanjun

from itsnp.core import Client
from itsnp.utils.permissions import Permissions

component = tanjun.Component()
permissions = Permissions()

emoji_group = tanjun.slash_command_group("emoji", "Group that handles emoji operations")


@emoji_group.with_command
@tanjun.with_str_slash_option("name", "Name of the emoji")
@tanjun.with_str_slash_option("url", "URL of the Emoji to be created.")
@tanjun.as_slash_command("create", "Create an emoji in the guild")
async def create_emoji(ctx: tanjun.abc.Context, url: str, name: str) -> None:
    guild = ctx.get_guild()
    await permissions.staff_role_check(ctx, guild)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            try:
                if r.status in range(200, 299):
                    emj = io.BytesIO(await r.read())
                    bytes = emj.getvalue()
                    emoji = await ctx.rest.create_emoji(
                        ctx.get_guild(), name, image=bytes
                    )
                    await ctx.respond(f"I created the emoji successfully | {emoji}")
                else:
                    await ctx.respond(f"Error making request | Response: {r.status}")
            except hikari.BadRequestError:
                await ctx.respond("File size may be too big.")


@emoji_group.with_command
@tanjun.with_str_slash_option("new_name", "New Name of the Emoji")
@tanjun.with_str_slash_option("emoji_id", "ID of the Emoji to be renamed")
@tanjun.as_slash_command("rename", "Rename an emoji of the server")
async def rename_emoji(ctx: tanjun.abc.Context, emoji_id: str, new_name: str) -> None:
    guild = ctx.get_guild()
    await permissions.staff_role_check(ctx, guild)
    emoji = await ctx.rest.fetch_emoji(guild, emoji_id)
    await ctx.respond(
        f"I changed the name of the emoji from `{emoji.name}`to `{new_name}`"
    )
    await ctx.rest.edit_emoji(guild, emoji, name=new_name)


@emoji_group.with_command
@tanjun.with_str_slash_option("emoji_id", "ID of the Emoji to be deleted")
@tanjun.as_slash_command("delete", "Delete an emoji from the server")
async def delete_emoji(ctx: tanjun.abc.Context, emoji_id: str) -> None:
    guild = ctx.get_guild()
    await permissions.staff_role_check(ctx, guild)
    emoji = await ctx.rest.fetch_emoji(guild, emoji_id)
    await ctx.respond(f"I deleted the emoji sucessfully | {emoji}")
    await ctx.rest.delete_emoji(guild, emoji)


component.add_slash_command(emoji_group)


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(component.copy())
