import typing as t
from datetime import datetime

import hikari
import tanjun
from hikari.events.member_events import MemberCreateEvent

from itsnp.core import Client
from itsnp.utils.permissions import Permissions
from models import MemberJoinModel

component = tanjun.Component()
permissions = Permissions()


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.MANAGE_CHANNELS
    | hikari.Permissions.MANAGE_GUILD
)
@tanjun.with_channel_slash_option(
    "channel", "The channel you want to set as Welcome Channel"
)
@tanjun.as_slash_command(
    "setwelcomechannel",
    "Set a Welcome Channel for the guild",
    default_to_ephemeral=True,
)
async def set_welcome_channel(
    ctx: tanjun.abc.Context, channel: hikari.GuildTextChannel
) -> None:
    await permissions.admin_role_check(ctx, ctx.get_guild())
    model, _ = await MemberJoinModel.get_or_create(
        guild_id=ctx.guild_id, channel_id=channel.id
    )
    await model.save()
    embed = hikari.Embed(
        title="Configuration",
        description=f"The Welcome Channel for this guild has been set to {channel}",
        timestamp=datetime.now().astimezone(),
        color=0x00FF00,
    )
    embed.set_thumbnail(ctx.get_guild().icon_url)
    await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.MANAGE_ROLES
    | hikari.Permissions.MANAGE_GUILD
)
@tanjun.with_str_slash_option(
    "message", "The Welcome message for the server", default=None
)
@tanjun.as_slash_command(
    "setwelcomemessage", "Set welcome message for the guild.", default_to_ephemeral=True
)
async def set_welcome_message(
    ctx: tanjun.abc.Context, message: t.Optional[str]
) -> None:
    await permissions.admin_role_check(ctx, ctx.get_guild())
    default = "Enjoy your stay here"
    welcome = await MemberJoinModel.get_or_none(guild_id=ctx.guild_id)
    welcome.welcome_message = message
    await welcome.save()
    embed = hikari.Embed(
        title="Configuration",
        description=f"The welcome message for {ctx.get_guild()} has been set to `{message if message else default}`",
        timestamp=datetime.now().astimezone(),
        color=0x00FF00,
    )
    embed.set_thumbnail(ctx.get_guild().icon_url)
    await ctx.respond(embed=embed)


@component.with_listener(hikari.MemberCreateEvent)
async def on_member_join(event: hikari.MemberCreateEvent) -> None:
    if not event.member.user.is_bot:
        default = "Enjoy your stay here."
        query = await MemberJoinModel.get_or_none(guild_id=event.guild_id)
        message = query.welcome_message
        guild = event.get_guild()
        channel = guild.get_channel(query.channel_id)
        try:
            if guild.get_member(event.member.user.id) is not None:
                embed = hikari.Embed(
                    title=f"Hello {event.member.username}, Welcome to {guild}.",
                    description=message if message else default,
                    color=0x00FF00,
                    timestamp=datetime.now().astimezone(),
                )
                embed.set_thumbnail(event.member.avatar_url)
                embed.set_author(
                    name=f"{guild.get_my_member()}",
                    icon=guild.get_my_member().avatar_url,
                )
                fields = [
                    (
                        "Created On",
                        f"<t:{int(event.member.created_at.timestamp())}:F> • <t:{int(event.member.created_at.timestamp())}:R>",
                        True,
                    )
                ]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                await channel.send(
                    event.member.mention, embed=embed, user_mentions=True
                )
        except:
            pass


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(component.copy())
