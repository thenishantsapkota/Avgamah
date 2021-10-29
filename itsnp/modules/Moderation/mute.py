import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.time import TimeConverter

from . import mute_handler, permissions

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
@tanjun.with_member_slash_option("member", "Member to mutes")
@tanjun.as_slash_command("mute", "Mute the user from the server.")
async def mute_command(
    ctx: tanjun.abc.Context, member: hikari.Member, time: str, reason: str
) -> None:
    guild = ctx.get_guild()
    time_seconds = await TimeConverter.convert(TimeConverter, ctx, time)
    await permissions.staff_role_check(ctx, guild)
    await mute_handler(ctx, member, time_seconds, reason)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(mute_component.copy())
