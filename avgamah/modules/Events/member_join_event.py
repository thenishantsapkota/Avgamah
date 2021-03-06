import logging
from datetime import datetime

import hikari
import tanjun

from avgamah.core import Client
from avgamah.utils.utilities import get
from models import MemberJoinModel, MuteModel

component = tanjun.Component()


@component.with_listener(hikari.MemberCreateEvent)
async def on_member_join(event: hikari.MemberCreateEvent) -> None:
    if not event.member.user.is_bot:
        default = "Enjoy your stay here."
        muted_role = get(await event.app.rest.fetch_roles(event.guild_id), name="Muted")
        mute_query = await MuteModel.get_or_none(member_id=event.member.id)
        try:
            if mute_query.member_id == event.member.id:
                await event.member.edit(
                    roles=[muted_role], reason="Member was muted previously"
                )
        except Exception as e:
            logging.info(f"Exception {e} occured in {event.get_guild()}")
            pass
        query = await MemberJoinModel.get_or_none(guild_id=event.guild_id)
        if query:
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
        except Exception as e:
            logging.info(f"Exception {e} occured in {event.get_guild()}")
            pass


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(component.copy())
