import hikari
import lavasnek_rs
import tanjun

from itsnp.core.client import Client
from itsnp.utils.spotify import get_songs

from . import SPOTIFY_PLAYLIST, URL_REGEX, _join

play_component = tanjun.Component()


@play_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.with_str_slash_option("query", "Name of the song or URL")
@tanjun.as_slash_command("play", "Play a song")
async def play(ctx: tanjun.abc.Context, query: str) -> None:
    con = await ctx.shards.data.lavalink.get_guild_gateway_connection_info(ctx.guild_id)

    if not con:
        await _join(ctx)

    # if SPOTIFY_PLAYLIST.match(query):
    #     songs = await get_songs(query)
    #     await ctx.respond("Loading Playlist...\nThis may take some time.")
    #     for song in songs:
    #         query_information = await ctx.shards.data.lavalink.search_tracks(song)
    #         try:
    #             await ctx.shards.data.lavalink.play(
    #                 ctx.guild_id, query_information.tracks[0]
    #             ).requester(ctx.author.id).queue()
    #             node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)
    #             if not node:
    #                 pass
    #             else:
    #                 await node.set_data({ctx.guild_id: ctx.channel_id})
    #         except lavasnek_rs.NoSessionPresent:
    #             return await ctx.respond("Use `/join` to run this command.")

    #     await ctx.edit_last_response(f"Added Spotify Playlist `{query}` to the queue.")

    query_information = await ctx.shards.data.lavalink.auto_search_tracks(query)

    if not query_information.tracks:
        return await ctx.respond("I could not find any songs according to the query!")

    try:
        if not URL_REGEX.match(query):
            await ctx.shards.data.lavalink.play(
                ctx.guild_id, query_information.tracks[0]
            ).requester(ctx.author.id).queue()
            node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)
        else:
            for track in query_information.tracks:
                await ctx.shards.data.lavalink.play(ctx.guild_id, track).requester(
                    ctx.author.id
                ).queue()
            node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

        if not node:
            pass
        else:
            await node.set_data({ctx.guild_id: ctx.channel_id})
    except lavasnek_rs.NoSessionPresent:
        return await ctx.respond("Use `/join` to run this command.")

    embed = hikari.Embed(
        title="Tracks Added",
        description=f"[{query_information.tracks[0].info.title}]({query_information.tracks[0].info.uri})",
        color=0x00FF00,
    )
    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(play_component.copy())
