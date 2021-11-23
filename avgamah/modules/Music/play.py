from datetime import timedelta

import hikari
import lavasnek_rs
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW
from avgamah.utils.time import pretty_timedelta

from . import URL_REGEX, _join, fetch_lavalink

play_component = tanjun.Component()


@play_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.with_bool_slash_option(
    "spotify", "Choose if the link is a spotify link.", default=None
)
@tanjun.with_str_slash_option("query", "Name of the song or URL")
@tanjun.as_slash_command("play", "Play a song")
async def play(ctx: tanjun.abc.Context, query: str, spotify: bool) -> None:
    length = 0
    lavalink = fetch_lavalink(ctx)

    con = await lavalink.get_guild_gateway_connection_info(ctx.guild_id)

    if not con:
        await _join(ctx)

    if spotify:
        raise tanjun.CommandError("Not Implemented Yet!")
    query_information = await lavalink.auto_search_tracks(query)

    if not query_information.tracks:
        return await ctx.respond(
            "I could not find any songs according to the query!", component=DELETE_ROW
        )

    try:
        if not URL_REGEX.match(query):
            await lavalink.play(ctx.guild_id, query_information.tracks[0]).requester(
                ctx.author.id
            ).queue()
        else:
            for track in query_information.tracks:
                length += track.info.length
                await lavalink.play(ctx.guild_id, track).requester(
                    ctx.author.id
                ).queue()

        node = await lavalink.get_guild_node(ctx.guild_id)

        if not node:
            pass
        else:
            await node.set_data({ctx.guild_id: ctx.channel_id})
    except lavasnek_rs.NoSessionPresent:
        return await ctx.respond("Use `/join` to run this command.")

    if URL_REGEX.match(query):
        embed = (
            hikari.Embed(
                title="Added a Playlist",
                description=f"[{query_information.playlist_info.name}]({query})",
                color=0x00FF00,
            )
            .add_field("Playtime", pretty_timedelta(timedelta(seconds=length / 1000)))
            .set_thumbnail(
                "https://static.vecteezy.com/system/resources/previews/002/238/014/original/playlist-icon-on-white-line-vector.jpg"
            )
        )
    else:
        embed = hikari.Embed(
            title="Tracks Added",
            description=f"[{query_information.tracks[0].info.title}]({query_information.tracks[0].info.uri})",
            color=0x00FF00,
        ).set_thumbnail(
            "https://cdn.discordapp.com/attachments/853173570107342858/911225696993542224/music-player-song-pngrepo-com.png"
        )
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(play_component.copy())
