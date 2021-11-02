from datetime import datetime

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW

from . import permissions

unban_component = tanjun.Component()


@unban_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.BAN_MEMBERS
    | hikari.Permissions.MANAGE_ROLES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("reason", "Reason to Unban the user")
@tanjun.with_str_slash_option("user_id", "ID of the user that needs to be unbanned.")
@tanjun.as_slash_command("unban", "Unban a member from the Guild")
async def unban_command(ctx: tanjun.abc.Context, user_id: int, reason: str) -> None:
    guild = ctx.get_guild()
    await permissions.admin_role_check(ctx, guild)
    log_channel = await permissions.log_channel_check(ctx, guild)
    user = await ctx.rest.fetch_user(user_id)
    await guild.unban(user, reason=reason)
    embed = hikari.Embed(
        color=0x00FF00,
        timestamp=datetime.now().astimezone(),
        description=f"🔓 **Unbanned {user}** [ ID {user.id}]\n📄**Reason:**{reason}",
    )
    embed.set_thumbnail(ctx.member.avatar_url)
    embed.set_author(
        name=f"{ctx.member} [ ID {ctx.member.id}]", icon=ctx.member.avatar_url
    )
    await log_channel.send(embed=embed)
    await ctx.respond(f"🔓 ** Unbanned `{user}`**", component=DELETE_ROW)
    try:
        await user.send(f"🔓 Unbanned from {guild.name}\n📄Reason: {reason}")

    except hikari.ForbiddenError:
        pass


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(unban_component.copy())
