import io

import aiohttp
import hikari
import tanjun

from itsnp.core.client import Client

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
                    await ctx.respond(f"I created the emoji successfully | {emoji}")
                else:
                    await ctx.respond(f"Error making request | Response: {r.status}")
            except hikari.BadRequestError:
                await ctx.respond("File size may be too big.")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(emoji_create_component.copy())
