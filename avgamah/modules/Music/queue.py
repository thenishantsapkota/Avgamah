from datetime import datetime, time, timedelta

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.pagination import paginate
from avgamah.utils.time import pretty_timedelta, pretty_timedelta_shortened
from avgamah.utils.utilities import _chunk

from . import fetch_lavalink

queue_component = tanjun.Component()


@queue_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("queue", "Shows the music queue")
async def queue(ctx: tanjun.abc.Context) -> None:
    song_queue = []
    length = 0
    lavalink = fetch_lavalink(ctx)
    node = await lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        return await ctx.respond("There are no tracks in the queue!")

    for song in node.queue:
        length += song.track.info.length
        song_queue += [
            f"`{pretty_timedelta_shortened(timedelta(seconds=song.track.info.length))}` [{song.track.info.title}]({song.track.info.uri}) [<@{song.requester}>]"
        ]

    fields = []
    counter = 1
    if not len(song_queue[1:]) > 0:
        return await ctx.respond(
            f"No tracks in the queue.\n**Now Playing** : [{node.now_playing.track.info.title}]({node.now_playing.track.info.uri})"
        )
    for index, track in enumerate(_chunk(song_queue[1:], 8)):
        string = """**Next Up**\n"""
        temp = []
        for i in track:
            string += f"""**{counter})** {i}\n"""

            counter += 1
        embed = hikari.Embed(
            title=f"Queue for {ctx.get_guild()}",
            color=0x00FF00,
            timestamp=datetime.now().astimezone(),
            description=string,
        )
        embed.set_footer(text=f"Page {index+1}")
        embed.add_field(
            name="Playtime",
            value=pretty_timedelta(timedelta(seconds=length / 1000)),
            inline=True,
        )
        embed.add_field(name="Entries", value=len(song_queue[1:]), inline=True)
        embed.add_field(
            name="Now Playing",
            value=f"[{node.now_playing.track.info.title}]({node.now_playing.track.info.uri}) [<@{node.now_playing.requester}>]",
        )
        temp.append(hikari.UNDEFINED)
        temp.append(embed)
        fields.append(temp)

    iter_fields = iter(fields)

    await paginate(ctx, iter_fields, 180)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(queue_component.copy())
