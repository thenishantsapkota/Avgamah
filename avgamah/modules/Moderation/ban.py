from datetime import datetime

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import permissions

ban_component = tanjun.Component()


@ban_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.BAN_MEMBERS
    | hikari.Permissions.MANAGE_ROLES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("reason", "Reason to ban the member")
@tanjun.with_member_slash_option("member", "Member to ban")
@tanjun.as_slash_command("ban", "Ban a member from the server.")
async def ban_command(
    ctx: tanjun.abc.Context, member: hikari.Member, reason: str
) -> None:
    guild = ctx.get_guild()
    await permissions.mod_role_check(ctx, guild)
    log_channel = await permissions.log_channel_check(ctx, guild)
    await permissions.check_higher_role(ctx.member, member)
    await guild.ban(member.user, reason=reason)
    embed = hikari.Embed(
        color=0xFF0000,
        timestamp=datetime.now().astimezone(),
        description=f"🔨 **Banned {member}** [ ID {member.id}]\n📄**Reason:**{reason}",
    )
    embed.set_thumbnail(member.avatar_url)
    embed.set_author(
        name=f"{ctx.member} [ ID {ctx.member.id}]", icon=ctx.member.avatar_url
    )
    await log_channel.send(embed=embed)
    await ctx.respond(f"🔨 ** Banned `{member}`**", component=DELETE_ROW)
    try:
        await member.send(f"🔨 Banned from {guild.name}\n📄Reason: {reason}")

    except hikari.ForbiddenError:
        pass


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(ban_component.copy())
