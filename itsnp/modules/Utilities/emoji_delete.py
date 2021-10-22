from datetime import datetime

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import create_source_button

from . import emoji_group, permissions

emoji_delete_component = tanjun.Component()


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
    await ctx.respond(f"I deleted the emoji sucessfully | {emoji}")
    await ctx.rest.delete_emoji(guild, emoji)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(emoji_delete_component.copy())
