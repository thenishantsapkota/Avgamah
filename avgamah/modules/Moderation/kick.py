import hikari
import tanjun

from avgamah.core.client import Client

from . import kick_handler, permissions

kick_component = tanjun.Component()


@kick_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.KICK_MEMBERS
    | hikari.Permissions.MANAGE_ROLES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("reason", "Reason to kick the member.")
@tanjun.with_member_slash_option("member", "A member to kick")
@tanjun.as_slash_command("kick", "Kick the user from the server")
async def kick_command(
    ctx: tanjun.abc.Context, member: hikari.Member, reason: str
) -> None:
    guild = ctx.get_guild()
    await permissions.mod_role_check(ctx, guild)
    await kick_handler(ctx, member, reason)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(kick_component.copy())
