import asyncio
from datetime import datetime

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.time import *
from models import MuteModel

from . import mute_handler, permissions, unmute_handler

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


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(mute_component.copy())
