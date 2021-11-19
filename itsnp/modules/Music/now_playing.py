from datetime import timedelta

import hikari
import lavasnek_rs
import tanjun

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
    node: lavasnek_rs.Node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond(
            "There's nothing playing at the moment!", component=DELETE_ROW
        )
    total = pretty_timedelta_shortened(
        timedelta(seconds=node.now_playing.track.info.length / 1000)
    )
    now = pretty_timedelta_shortened(
        timedelta(seconds=node.now_playing.track.info.position / 1000)
    )

    embed = hikari.Embed(
        title="Now Playing",
        description=f"[{node.now_playing.track.info.title}]({node.now_playing.track.info.uri})",
        color=0x00FF00,
    )
    fields = [
        ("Requested by", f"<@{node.now_playing.requester}>", True),
        ("Author", node.now_playing.track.info.author, True),
        ("Duration", f"{now}/{total}", True),
    ]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(now_playing_component.copy())
