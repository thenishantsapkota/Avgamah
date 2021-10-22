import asyncio
from datetime import datetime, timedelta

import hikari
import tanjun

from itsnp.utils.permissions import Permissions
from itsnp.utils.time import *
from models import MuteModel, WarningsModel

permissions = Permissions()


async def warning_count(ctx: tanjun.abc.Context, member: hikari.Member) -> None:
    """Function that checks for number of warnings a user has"""
    warn_model = await WarningsModel.filter(guild_id=ctx.guild_id, member_id=member.id)

    if len(warn_model) in range(5, 8):
        await mute_handler(ctx, member, 600, f"Warning Count : {len(warn_model)}")

    if len(warn_model) in range(8, 10):
        await mute_handler(ctx, member, 21600, f"Warning Count : {len(warn_model)}")

    if len(warn_model) >= 10:
        await kick_handler(ctx, member, f"Warning Count : {len(warn_model)}")


async def mute_handler(
    ctx: tanjun.abc.Context, member: hikari.Member, time: float, reason: str
) -> None:
    muted_role = await permissions.muted_role_check(ctx, ctx.get_guild())
    log_channel = await permissions.log_channel_check(ctx, ctx.get_guild())
    await permissions.check_higher_role(ctx.member, member)
    unmutes = []
    pretty_time = pretty_timedelta(timedelta(seconds=time))
    booster_role = await permissions.check_booster_role(member)

    if muted_role not in await member.fetch_roles():
        end_time = datetime.now() + timedelta(seconds=time)
        role_ids = ",".join([str(r) for r in member.role_ids])
        model, _ = await MuteModel.get_or_create(
            guild_id=ctx.get_guild().id,
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
        embed = hikari.Embed(
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

        if time:
            unmutes.append(member)

    else:
        await ctx.respond("Member is already muted!")

    try:
        await member.send(
            f"🔇 Muted from {ctx.get_guild().name} \nReason:{reason}.\nTime: {pretty_time}"
        )

    except hikari.ForbiddenError:
        pass

    if len(unmutes):
        await asyncio.sleep(time)
        updated_member = await ctx.rest.fetch_member(ctx.get_guild(), member.user)
        await unmute_handler(ctx, updated_member)


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
        Member that needs to be unmuted
    reason : str, optional
        Reason to unmute the member., by default "Mute Duration Expired"
    """
    guild = ctx.get_guild()
    muted_role = await permissions.muted_role_check(ctx, guild)
    log_channel = await permissions.log_channel_check(ctx, guild)
    if muted_role.id not in member.role_ids:
        return await ctx.respond(f"***User seems to be already unmuted!***")

    model = await MuteModel.get_or_none(guild_id=guild.id, member_id=member.id)
    role_ids = model.role_id
    roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]
    await model.delete()
    await member.edit(roles=roles, reason="Unmuted the user.")
    embed = hikari.Embed(
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

    try:
        await member.send(f"🔊 Unmuted from {guild.name}")

    except hikari.ForbiddenError:
        pass


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
    embed = hikari.Embed(
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

    except hikari.ForbiddenError:
        pass
