import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.time import TimeConverter

from . import self_mute_handler

mute_component = tanjun.Component()


@mute_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_MESSAGES
    | hikari.Permissions.MANAGE_ROLES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("reason", "Reason to mute the user")
@tanjun.with_str_slash_option("time", "Time to mute the user for")
@tanjun.as_slash_command(
    "selfmute", "Mute yourself, Don't bug the mods for being muted."
)
async def self_mute_command(ctx: tanjun.abc.Context, time: str, reason: str) -> None:
    time_seconds = await TimeConverter.convert(TimeConverter, ctx, time)
    await self_mute_handler(ctx, ctx.member, time_seconds, reason)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(mute_component.copy())
