import io

import aiohttp
import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW

from . import emoji_group, permissions

emoji_create_component = tanjun.Component()


@emoji_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.READ_MESSAGE_HISTORY
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.MANAGE_EMOJIS_AND_STICKERS
)
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
                    await ctx.respond(
                        f"I created the emoji successfully | {emoji}",
                        component=DELETE_ROW,
                    )
                else:
                    await ctx.respond(
                        f"Error making request | Response: {r.status}",
                        component=DELETE_ROW,
                    )
            except hikari.BadRequestError:
                await ctx.respond("File size may be too big.", component=DELETE_ROW)


@emoji_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.READ_MESSAGE_HISTORY
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.MANAGE_EMOJIS_AND_STICKERS
)
@tanjun.with_str_slash_option("emoji_id", "ID of the Emoji to be deleted")
@tanjun.as_slash_command("delete", "Delete an emoji from the server")
async def delete_emoji(ctx: tanjun.abc.Context, emoji_id: str) -> None:
    guild = ctx.get_guild()
    await permissions.staff_role_check(ctx, guild)
    emoji = await ctx.rest.fetch_emoji(guild, emoji_id)
    await ctx.respond(
        f"I deleted the emoji sucessfully | {emoji}", component=DELETE_ROW
    )
    await ctx.rest.delete_emoji(guild, emoji)


@emoji_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.READ_MESSAGE_HISTORY
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.MANAGE_EMOJIS_AND_STICKERS
)
@tanjun.with_str_slash_option("new_name", "New Name of the Emoji")
@tanjun.with_str_slash_option("emoji_id", "ID of the Emoji to be renamed")
@tanjun.as_slash_command("rename", "Rename an emoji of the server")
async def rename_emoji(ctx: tanjun.abc.Context, emoji_id: str, new_name: str) -> None:
    guild = ctx.get_guild()
    await permissions.staff_role_check(ctx, guild)
    emoji = await ctx.rest.fetch_emoji(guild, emoji_id)
    await ctx.respond(
        f"I changed the name of the emoji from `{emoji.name}`to `{new_name}`",
        component=DELETE_ROW,
    )
    await ctx.rest.edit_emoji(guild, emoji, name=new_name)


emoji_create_component.add_slash_command(emoji_group)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(emoji_create_component.copy())
