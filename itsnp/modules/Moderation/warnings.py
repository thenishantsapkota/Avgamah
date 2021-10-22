import asyncio
from datetime import datetime

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.pagination import paginate
from itsnp.utils.time import *
from itsnp.utils.utilities import _chunk
from models import WarningsModel

from . import permissions

warnings_component = tanjun.Component()

warnings_group = tanjun.slash_command_group("warnings", "Group that handles warnings")


@warnings_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_MESSAGES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_member_slash_option("member", "Member whose warnings you wanna see.")
@tanjun.as_slash_command("list", "List the warnings of a member")
async def warnings_list(ctx: tanjun.abc.Context, member: hikari.Member) -> None:
    author = ctx.member
    guild = ctx.get_guild()
    await permissions.staff_role_check(ctx, guild)
    warn_model = await WarningsModel.filter(guild_id=guild.id, member_id=member.id)

    if not len(warn_model):
        return await ctx.respond("User hasn't been warned!")

    warnings = [
        f"#{model.id} - `{model.date}` - Warned By **{model.author_name}**\n**Reason:**{model.reason}"
        for model in warn_model
    ]
    fields = (
        (
            hikari.UNDEFINED,
            hikari.Embed(
                color=0x00FF00,
                timestamp=datetime.now().astimezone(),
                title=f"Warnings-{member}[ID - {member.id}]",
                description="\n\n".join(warning),
            ).set_footer(text=f"Requested by {author} | Page: {index+1}"),
        )
        for index, warning in enumerate(_chunk(warnings, 5))
    )

    await paginate(ctx, fields, 180)


@warnings_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_MESSAGES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_int_slash_option("id", "ID of the Warning")
@tanjun.with_member_slash_option("member", "Member whose warning is to be deleted")
@tanjun.as_slash_command("delete", "Delete one warning of a user")
async def warnings_delete(
    ctx: tanjun.abc.Context, member: hikari.Member, id: int
) -> None:
    author = ctx.member
    await permissions.mod_role_check(ctx, ctx.get_guild())
    log_channel = await permissions.log_channel_check(ctx, ctx.get_guild())
    model = await WarningsModel.get_or_none(guild_id=ctx.guild_id, id=id)
    if model is None:
        return await ctx.respond("Warning ID doesn't exist!")
    await model.delete()
    await ctx.respond(f"Deleted Warning #{id} of **{member}**")
    embed = hikari.Embed(
        color=0x00FF00,
        timestamp=datetime.utcnow(),
        description=f"⚠️ Deleted Warning #{id} of \n**{member} [ID {member.id}]**",
    )
    embed.set_author(name=f"{author} [ID {author.id}]", icon=author.avatar_url)
    embed.set_thumbnail(url=member.avatar_url)
    await log_channel.send(embed=embed)


@warnings_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_MESSAGES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_member_slash_option("member", "Member whose warnings are to be cleared")
@tanjun.as_slash_command("clear", "Clear warnings of a user")
async def warnings_clear(ctx: tanjun.abc.Context, member: hikari.Member) -> None:
    author = ctx.member
    guild = ctx.get_guild()
    await permissions.admin_role_check(ctx, guild)
    log_channel = await permissions.log_channel_check(ctx, guild)
    await WarningsModel.filter(guild_id=guild.id, member_id=member.id).delete()
    await ctx.respond(f"Cleared Warnings of **{member}**")
    embed = hikari.Embed(
        color=0x00FF00,
        timestamp=datetime.utcnow(),
        description=f"⚠️ Cleared Warnings of \n**{member} [ID {member.id}]**",
    )
    embed.set_author(name=f"{author} [ID {author.id}]", icon=author.avatar_url)
    embed.set_thumbnail(member.avatar_url)
    await log_channel.send(embed=embed)


warnings_component.add_slash_command(warnings_group)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(warnings_component.copy())
