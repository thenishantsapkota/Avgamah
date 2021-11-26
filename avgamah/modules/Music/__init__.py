import asyncio
import re

import hikari
import lavasnek_rs
import tanjun

# from avgamah.utils import spotify
from avgamah.utils.buttons import DELETE_ROW
from avgamah.utils.spotify import get_tracks_from_playlist
from config import spotify_config

# from config import spotify_config

TIME_REGEX = r"([0-9]{1,2})[:ms](([0-9]{1,2})s?)?"

URL_REGEX = re.compile(r"^.*(youtu.be\/|list=)([^#\&\?]*).*")

SPOTIFY_PLAYLIST = re.compile(
    r"[\bhttps://open.\b]*spotify[\b.com\b]*[/:]*playlist[/:]*[A-Za-z0-9?=]+"
)


def check_voice_state(f):
    async def predicate(ctx: tanjun.abc.Context, *args, **kwargs):
        guild = ctx.get_guild()
        bot_user = await ctx.rest.fetch_my_user()

        voice_state_bot = ctx.cache.get_voice_state(guild, bot_user)
        voice_state_author = ctx.cache.get_voice_state(guild, ctx.author)

        if voice_state_bot is None:
            raise tanjun.CommandError(
                "I am not connected to any Voice Channel.\nUse `/join` to connect me to one."
            )

        if voice_state_author is None:
            raise tanjun.CommandError(
                "You are not in a Voice Channel, Join a Voice Channel to continue."
            )

        if not voice_state_author.channel_id == voice_state_bot.channel_id:
            raise tanjun.CommandError(
                "I cannot run this command as you are not in the same voice channel as me."
            )

        return await f(ctx, *args, **kwargs)

    return predicate


async def _join(ctx: tanjun.abc.Context) -> int:
    lavalink = fetch_lavalink(ctx)
    if ctx.cache.get_voice_state(ctx.get_guild(), await ctx.rest.fetch_my_user()):
        raise tanjun.CommandError("I am already connected to another Voice Channel.")

    states = ctx.cache.get_voice_states_view_for_guild(ctx.get_guild())
    voice_state = list(filter(lambda i: i.user_id == ctx.author.id, states.iterator()))

    if not voice_state:
        raise tanjun.CommandError("Connect to a voice channel to continue!")

    channel_id = voice_state[0].channel_id

    try:
        connection_info = await lavalink.join(ctx.guild_id, channel_id)

    except TimeoutError:
        raise tanjun.CommandError("I cannot connect to your voice channel!")

    await lavalink.create_session(connection_info)
    return channel_id


async def _leave(ctx: tanjun.abc.Context):
    lavalink = fetch_lavalink(ctx)
    await lavalink.destroy(ctx.guild_id)
    await lavalink.stop(ctx.guild_id)
    await lavalink.leave(ctx.guild_id)
    await lavalink.remove_guild_node(ctx.guild_id)
    await lavalink.remove_guild_from_loops(ctx.guild_id)

    embed = hikari.Embed(
        description="I left the voice channel!",
        color=0xFF0000,
    )
    await ctx.respond(embed=embed, component=DELETE_ROW)


def fetch_lavalink(ctx: tanjun.abc.Context) -> lavasnek_rs.Lavalink:
    return ctx.shards.data.lavalink


async def handle_spotify(ctx: tanjun.abc.Context, url: str) -> None:
    lavalink = fetch_lavalink(ctx)
    songs = await get_tracks_from_playlist(url)
    await ctx.respond(
        "Loading the Spotify Playlist...\nThis may take some time depending on the size of your playlist."
    )

    tracks = [(await lavalink.auto_search_tracks(song)).tracks[0] for song in songs]

    for track in tracks:
        try:
            await lavalink.play(ctx.guild_id, track).requester(ctx.author.id).queue()

            node = await lavalink.get_guild_node(ctx.guild_id)
            if not node:
                pass
            else:
                node.set_data({ctx.guild_id: ctx.channel_id})
        except lavasnek_rs.NoSessionPresent:
            raise tanjun.CommandError("Use `/join` to run this command.")

    await ctx.edit_last_response(f"Added Spotify Playlist `{url}` to the queue.")
