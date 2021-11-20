from datetime import datetime

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import permissions, role_group

remove_role_component = tanjun.Component()


@role_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.MANAGE_ROLES
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_role_slash_option("role", "Role to remove from the member")
@tanjun.with_member_slash_option("member", "Member from whom role is to be taken")
@tanjun.as_slash_command("take", "Take a role to a member")
async def take_role_command(
    ctx: tanjun.abc.Context, member: hikari.Member, role: hikari.Role
) -> None:
    guild = ctx.get_guild()
    author = ctx.member
    await permissions.mod_role_check(ctx, guild)
    await member.remove_role(role)
    embed = hikari.Embed(
        title=f"Updated Roles for {member}",
        color=role.color,
        timestamp=datetime.now().astimezone(),
    )
    embed.add_field(name="Removed Role", value=f"{role.mention}")
    embed.set_author(name=f"{author} [ {author.id} ]", icon=author.avatar_url)
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(remove_role_component.copy())
