from datetime import datetime

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW
from models import ModerationRoles

from . import role_group

roles_component = tanjun.Component()


@role_group.with_command
@tanjun.with_guild_check
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS,
)
@tanjun.with_role_slash_option("role", "Role or role id of admin role")
@tanjun.as_slash_command("admin", "Set admin role for the server.")
async def admin_role_command(ctx: tanjun.abc.Context, role: hikari.Role) -> None:
    guild = ctx.get_guild()
    model, _ = await ModerationRoles.get_or_create(guild_id=ctx.guild_id)
    model.admin_role = role.id
    await model.save()
    embed = hikari.Embed(
        title="Admin Role",
        description=f"The admin role  for {guild.name} has been set to {role.mention}",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0x00FF00),
    )
    await ctx.respond(embed=embed, component=DELETE_ROW)


@role_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_role_slash_option("role", "Role or role id of mod role")
@tanjun.as_slash_command("mod", "Set mod role for the server.")
async def mod_role_command(ctx: tanjun.abc.Context, role: hikari.Role) -> None:
    guild = ctx.get_guild()
    model, _ = await ModerationRoles.get_or_create(guild_id=ctx.guild_id)
    model.mod_role = role.id
    await model.save()
    embed = hikari.Embed(
        title="Moderator Role",
        description=f"The mod role  for {guild.name} has been set to {role.mention}",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0x00FF00),
    )
    await ctx.respond(embed=embed, component=DELETE_ROW)


@role_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_role_slash_option("role", "Role or role id of staff role")
@tanjun.as_slash_command("staff", "Set staff role for the server.")
async def staff_role_command(ctx: tanjun.abc.Context, role: hikari.Role) -> None:
    guild = ctx.get_guild()
    model, _ = await ModerationRoles.get_or_create(guild_id=ctx.guild_id)
    model.staff_role = role.id
    await model.save()
    embed = hikari.Embed(
        title="Staff Role",
        description=f"The staff role  for {guild.name} has been set to {role.mention}",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0x00FF00),
    )
    await ctx.respond(embed=embed, component=DELETE_ROW)


roles_component.add_slash_command(role_group)


@role_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command("list", "List moderation roles for the server")
async def list_command(ctx: tanjun.abc.Context) -> None:
    guild = ctx.get_guild()
    model = await ModerationRoles.get_or_none(guild_id=guild.id)
    if model is None:
        return await ctx.respond("No data found.")

    embed = hikari.Embed(
        color=hikari.Color(0x00FF00),
        timestamp=datetime.now().astimezone(),
    )

    fields = [
        ("Admin Role", f"<@&{model.admin_role}>", True),
        ("Moderator Role", f"<@&{model.mod_role}>", True),
        ("Staff Role", f"<@&{model.staff_role}>", True),
    ]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_author(name=f"Staff Roles for {guild.name}", icon=guild.icon_url)
    embed.set_footer(text=f"Invoked by {ctx.author}")
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(roles_component.copy())
