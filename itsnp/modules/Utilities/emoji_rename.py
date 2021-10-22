import hikari
import tanjun

from itsnp.core.client import Client

from . import emoji_group, permissions

emoji_rename_component = tanjun.Component()


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
        f"I changed the name of the emoji from `{emoji.name}`to `{new_name}`"
    )
    await ctx.rest.edit_emoji(guild, emoji, name=new_name)


emoji_rename_component.add_slash_command(emoji_group)


@tanjun.as_loader
def load_modules(client: Client) -> None:
    client.add_component(emoji_rename_component.copy())
