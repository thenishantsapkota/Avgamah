from datetime import datetime

import hikari
import tanjun
from hikari import Embed

from itsnp.core.client import Client
from itsnp.utils.permissions import Permissions
from models import ModerationRoles

component = tanjun.Component()
permissions = Permissions()

role_group = tanjun.SlashCommandGroup(
    "role", "Set moderation roles for the server"
).add_check(
    tanjun.AuthorPermissionCheck(
        hikari.Permissions.ADMINISTRATOR,
        error_message="You need **Administrator** permission(s) to run this command.",
    )
)


@role_group.with_command
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
    embed = Embed(
        title="Admin Role",
        description=f"The admin role  for {guild.name} has been set to {role.mention}",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0x00FF00),
    )
    await ctx.respond(embed=embed)


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
    embed = Embed(
        title="Moderator Role",
        description=f"The mod role  for {guild.name} has been set to {role.mention}",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0x00FF00),
    )
    await ctx.respond(embed=embed)


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
    embed = Embed(
        title="Staff Role",
        description=f"The staff role  for {guild.name} has been set to {role.mention}",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0x00FF00),
    )
    await ctx.respond(embed=embed)


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

    embed = Embed(
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
    await ctx.respond(embed=embed)


@role_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.MANAGE_ROLES
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_role_slash_option("role", "Role to give the member")
@tanjun.with_member_slash_option("member", "Member to whom role is to be given")
@tanjun.as_slash_command("give", "Give a role to a member")
async def give_role_command(
    ctx: tanjun.abc.Context, member: hikari.Member, role: hikari.Role
) -> None:
    guild = ctx.get_guild()
    author = ctx.member
    await permissions.mod_role_check(ctx, guild)
    await member.add_role(role)
    embed = Embed(
        title=f"Updated Roles for {member}",
        color=role.color,
        timestamp=datetime.now().astimezone(),
    )
    embed.add_field(name="Added Role", value=f"{role.mention}")
    embed.set_author(name=f"{author} [ {author.id} ]", icon=author.avatar_url)
    await ctx.respond(embed=embed)


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
    embed = Embed(
        title=f"Updated Roles for {member}",
        color=role.color,
        timestamp=datetime.now().astimezone(),
    )
    embed.add_field(name="Removed Role", value=f"{role.mention}")
    embed.set_author(name=f"{author} [ {author.id} ]", icon=author.avatar_url)
    await ctx.respond(embed=embed)


component.add_slash_command(role_group)


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
