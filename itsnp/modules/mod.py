import asyncio
from datetime import datetime, timedelta
from typing import Optional

import hikari
import tanjun
from hikari.embeds import Embed

from itsnp.core.client import Client
from itsnp.core.models import MuteModel
from itsnp.utils.permissions import Permissions
from itsnp.utils.time import TimeConverter, pretty_timedelta

component = tanjun.Component()

permissions = Permissions()


@component.with_slash_command
@tanjun.with_str_slash_option("reason", "Reason to mute the user")
@tanjun.with_str_slash_option("time", "Time to mute the user for")
@tanjun.with_member_slash_option("member", "Member to mutes")
@tanjun.as_slash_command("mute", "Mute the user from the server.")
async def mute_command(
    ctx: tanjun.abc.Context, member: hikari.Member, time: str, *, reason: str
) -> None:
    author = ctx.member
    guild = ctx.get_guild()
    time_seconds = await TimeConverter.convert(TimeConverter, ctx, time)
    await permissions.staff_role_check(ctx, guild)
    muted_role = await permissions.muted_role_check(ctx, guild)
    log_channel = await permissions.log_channel_check(ctx, guild)
    await permissions.check_higher_role(author, member)
    unmutes = []
    pretty_time = pretty_timedelta(timedelta(seconds=time_seconds))
    booster_role = await permissions.check_booster_role(member)

    if muted_role not in await member.fetch_roles():
        end_time = datetime.now() + timedelta(seconds=time_seconds)
        role_ids = ",".join([str(r) for r in member.role_ids])
        model, _ = await MuteModel.get_or_create(
            guild_id=guild.id,
            member_id=member.id,
            time=end_time,
            role_id=role_ids,
        )
        await model.save()
        await member.edit(
            roles=[muted_role, booster_role], reason="Muted the user"
        ) if booster_role in member.get_roles() else await member.edit(
            roles=[muted_role], reason="Muted the user"
        )
        embed = Embed(
            description=f"🔇 **Muted {member}** [ ID {member.id}]\n📄**Reason:**{reason}",
            color=0xFF0000,
            timestamp=datetime.now().astimezone(),
        )
        embed.set_footer(text=f"Duration: {pretty_time}")
        embed.set_thumbnail(member.avatar_url)
        embed.set_author(
            name=f"{ctx.member} [ ID {ctx.member.id}]", icon=ctx.member.avatar_url
        )

        await log_channel.send(embed=embed)
        await ctx.respond(f"🔇 **Muted `{member}` for {pretty_time}**")

        if time_seconds:
            unmutes.append(member)

    else:
        await ctx.respond("Member is already muted!")

    try:
        await member.send(
            f"🔇 Muted from {guild.name} \nReason:{reason}.\nTime: {pretty_time}"
        )

    except hikari.BadRequestError:
        pass

    if len(unmutes):
        await asyncio.sleep(time_seconds)
        await unmute_handler(ctx, member)


@component.with_slash_command
@tanjun.with_str_slash_option("reason", "Reason to unmute the user", default=False)
@tanjun.with_member_slash_option("member", "Member to mutes")
@tanjun.as_slash_command("unmute", "Unmute a member from the server.")
async def unmute_command(
    ctx: tanjun.abc.Context,
    member: hikari.Member,
    *,
    reason: Optional[str] = "No reason provided.",
) -> None:
    await permissions.mod_role_check(ctx, ctx.get_guild())
    await unmute_handler(ctx, member, reason=reason)


async def unmute_handler(
    ctx: tanjun.abc.Context,
    member: hikari.Member,
    *,
    reason: str = "Mute Duration Expired",
) -> None:
    """Function that handles unmutes.add

    Parameters
    ----------
    ctx : tanjun.abc.Context
        Context of the Slash Command Invokation
    member : hikari.Member
        Member that needs to be unmuted.add
    reason : str, optional
        Reason to unmute the member., by default "Mute Duration Expired"
    """
    author = ctx.member
    guild = ctx.get_guild()
    muted_role = await permissions.muted_role_check(ctx, guild)
    log_channel = await permissions.log_channel_check(ctx, guild)
    if muted_role in await member.fetch_roles():
        model = await MuteModel.get_or_none(guild_id=guild.id, member_id=member.id)
        role_ids = model.role_id
        roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]
        await model.delete()
        await member.edit(roles=roles, reason="Unmuted the user.")
        embed = Embed(
            description=f"🔊 **Unmuted {member}** [ ID {member.id}]\n📄**Reason:**{reason}",
            color=0x00FF00,
            timestamp=datetime.now().astimezone(),
        )
        embed.set_thumbnail(member.avatar_url)
        embed.set_author(
            name=f"{ctx.member} [ ID {ctx.member.id}]", icon=ctx.member.avatar_url
        )

        await log_channel.send(embed=embed)
        await ctx.respond(f"**🔊 Unmuted {member}**")
    else:
        await ctx.respond(f"***User seems to be already unmuted!***")

    try:
        await member.send(f"🔊 Unmuted from {guild.name}")

    except hikari.BadRequestError:
        pass


@component.with_slash_command
@tanjun.with_str_slash_option("reason", "Reason to kick the member.")
@tanjun.with_member_slash_option("member", "A member to kick")
@tanjun.as_slash_command("kick", "Kick the user from the server")
async def kick_command(
    ctx: tanjun.abc.Context, member: hikari.Member, reason: str
) -> None:
    guild = ctx.get_guild()
    await permissions.mod_role_check(ctx, guild)
    await kick_handler(ctx, member, reason)


async def kick_handler(
    ctx: tanjun.abc.Context, member: hikari.Member, reason: str
) -> None:
    """
    Function that handles kicks.h

    Parameters
    ----------
    ctx : tanjun.abc.Context
        Context of Command Invokation
    member : hikari.Member
        Member that needs to be kicked.h
    reason : str
        Reason to kick the member.
    """
    log_channel = await permissions.log_channel_check(ctx, ctx.get_guild())
    await permissions.check_higher_role(ctx.member, member)
    await member.kick(reason=reason)
    embed = Embed(
        description=f"👢 **Kicked {member}** [ ID {member.id}]\n📄**Reason:**{reason}",
        color=0xFF0000,
        timestamp=datetime.now().astimezone(),
    )
    embed.set_thumbnail(member.avatar_url)
    embed.set_author(
        name=f"{ctx.member} [ ID {ctx.member.id}]", icon=ctx.member.avatar_url
    )
    await log_channel.send(embed=embed)
    await ctx.respond(f"👢 ** Kicked `{member}`**")
    try:
        await member.send(f"👢 Kicked from {ctx.get_guild().name}\n📄Reason: {reason}")

    except hikari.BadRequestError:
        pass


@component.with_slash_command
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
    embed = Embed(
        color=0xFF0000,
        timestamp=datetime.now().astimezone(),
        description=f"🔨 **Banned {member}** [ ID {member.id}]\n📄**Reason:**{reason}",
    )
    embed.set_thumbnail(member.avatar_url)
    embed.set_author(
        name=f"{ctx.member} [ ID {ctx.member.id}]", icon=ctx.member.avatar_url
    )
    await log_channel.send(embed=embed)
    await ctx.respond(f"🔨 ** Banned `{member}`**")
    try:
        await member.send(f"🔨 Banned from {guild.name}\n📄Reason: {reason}")

    except hikari.BadRequestError:
        pass


@component.with_slash_command
@tanjun.with_str_slash_option("reason", "Reason to Unban the user")
@tanjun.with_str_slash_option("user_id", "ID of the user that needs to be unbanned.")
@tanjun.as_slash_command("unban", "Unban a member from the Guild")
async def unban_command(ctx: tanjun.abc.Context, user_id: int, reason: str) -> None:
    guild = ctx.get_guild()
    await permissions.admin_role_check(ctx, guild)
    log_channel = await permissions.log_channel_check(ctx, guild)
    user = await ctx.rest.fetch_user(user_id)
    await guild.unban(user, reason=reason)
    embed = Embed(
        color=0x00FF00,
        timestamp=datetime.now().astimezone(),
        description=f"🔓 **Unbanned {user}** [ ID {user.id}]\n📄**Reason:**{reason}",
    )
    embed.set_thumbnail(ctx.member.avatar_url)
    embed.set_author(
        name=f"{ctx.member} [ ID {ctx.member.id}]", icon=ctx.member.avatar_url
    )
    await log_channel.send(embed=embed)
    await ctx.respond(f"🔓 ** Unbanned `{user}`**")
    try:
        await user.send(f"🔓 Unbanned from {guild.name}\n📄Reason: {reason}")

    except hikari.BadRequestError:
        pass


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
