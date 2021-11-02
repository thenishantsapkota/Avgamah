from datetime import timedelta

import hikari
import tanjun
from StringProgressBar import progressBar

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW
from itsnp.utils.time import pretty_timedelta_shortened

now_playing_component = tanjun.Component()


@now_playing_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("nowplaying", "See Currently Playing Song")
async def now_playing(ctx: tanjun.abc.Context) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond(
            "There's nothing playing at the moment!", component=DELETE_ROW
        )

    song_length = pretty_timedelta_shortened(
        timedelta(seconds=float(node.now_playing.track.info.length) / 1000)
    )

    current_position = pretty_timedelta_shortened(
        timedelta(seconds=float(node.now_playing.track.info.position) / 1000)
    )

    progress_bar = progressBar.createBoxDiscord(
        node.now_playing.track.info.position,
        node.now_playing.track.info.length,
        15,
    )

    embed = hikari.Embed(
        title="Now Playing",
        description=f"[{node.now_playing.track.info.title}]({node.now_playing.track.info.uri})",
        color=0x00FF00,
    )
    fields = [
        ("Requested by", f"<@{node.now_playing.requester}>", True),
        ("Author", node.now_playing.track.info.author, True),
        (
            "Progress",
            f"{progress_bar}\n**{current_position if current_position else '0s'} / {song_length}**",
            False,
        ),
    ]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(now_playing_component.copy())
