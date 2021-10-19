import random
import re
from datetime import datetime, timedelta

import aiohttp
import hikari
import lavasnek_rs
import tanjun
import yuyo
from hikari import Embed
from requests.api import get
from StringProgressBar import progressBar

from itsnp.core import Client
from itsnp.utils.pagination import paginate
from itsnp.utils.spotify import get_songs
from itsnp.utils.time import *
from itsnp.utils.utilities import _chunk

component = tanjun.Component()


URL_REGEX = re.compile(
    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
)

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
    if ctx.cache.get_voice_state(ctx.get_guild(), await ctx.rest.fetch_my_user()):
        raise tanjun.CommandError("I am already connected to another Voice Channel.")
    states = ctx.shards.cache.get_voice_states_view_for_guild(ctx.get_guild())
    voice_state = list(filter(lambda i: i.user_id == ctx.author.id, states.iterator()))

    if not voice_state:
        return await ctx.respond("Connect to a voice channel to continue!")

    channel_id = voice_state[0].channel_id

    try:
        connection_info = await ctx.shards.data.lavalink.join(ctx.guild_id, channel_id)

    except TimeoutError:
        return await ctx.respond("I cannot connect to your voice channel!")

    await ctx.shards.data.lavalink.create_session(connection_info)
    return channel_id


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("join", "Join a voice channel of a guild")
async def join(ctx: tanjun.abc.Context) -> None:
    channel_id = await _join(ctx)

    if channel_id:
        embed = Embed(description=f"Joined <#{channel_id}>", color=0x00FF00)
        await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("leave", "Leave the voice channel")
@check_voice_state
async def leave(ctx: tanjun.abc.Context) -> None:
    await ctx.shards.data.lavalink.destroy(ctx.guild_id)
    await ctx.shards.data.lavalink.stop(ctx.guild_id)
    await ctx.shards.data.lavalink.leave(ctx.guild_id)
    await ctx.shards.data.lavalink.remove_guild_node(ctx.guild_id)
    await ctx.shards.data.lavalink.remove_guild_from_loops(ctx.guild_id)

    embed = Embed(
        description=f"I left the voice channel!",
        color=0xFF0000,
    )
    await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("stop", "Stop the playback")
@check_voice_state
async def stop(ctx: tanjun.abc.Context) -> None:
    await ctx.shards.data.lavalink.stop(ctx.guild_id)

    embed = Embed(
        title="⏹️ Playback Stopped!",
        color=0xFF0000,
    )
    await ctx.respond(embed=embed)


@component.with_slash_command
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

    if SPOTIFY_PLAYLIST.match(query):
        songs = await get_songs(query)
        await ctx.respond("Loading Playlist...\nThis may take some time.")
        for song in songs:
            query_information = await ctx.shards.data.lavalink.search_tracks(song)
            try:
                await ctx.shards.data.lavalink.play(
                    ctx.guild_id, query_information.tracks[0]
                ).requester(ctx.author.id).queue()
                node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)
                if not node:
                    pass
                else:
                    await node.set_data({ctx.guild_id: ctx.channel_id})
            except lavasnek_rs.NoSessionPresent:
                return await ctx.respond("Use `/join` to run this command.")

        await ctx.edit_last_response(f"Added Spotify Playlist `{query}` to the queue.")

    else:
        query_information = await ctx.shards.data.lavalink.auto_search_tracks(query)

        if not query_information.tracks:
            return await ctx.respond(
                "I could not find any songs according to the query!"
            )

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

        embed = Embed(
            title="Tracks Added",
            description=f"[{query_information.tracks[0].info.title}]({query_information.tracks[0].info.uri})",
            color=0x00FF00,
        )
        await ctx.respond(embed=embed)


@component.with_slash_command
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
        return await ctx.respond("There's nothing playing at the moment!")

    song_length = pretty_timedelta_shortened(
        timedelta(seconds=float(node.now_playing.track.info.length) / 1000)
    )

    current_position = pretty_timedelta_shortened(
        timedelta(seconds=float(node.now_playing.track.info.position) / 1000)
    )

    progress_bar = progressBar.createBoxDiscord(
        node.now_playing.track.info.position, node.now_playing.track.info.length, 15
    )

    embed = Embed(
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
    await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("pause", "Pause the current song being played")
@check_voice_state
async def pause(ctx: tanjun.abc.Context) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond("There are no tracks currently playing!")

    if node.is_paused:
        return await ctx.respond("Playback is already paused!")

    await ctx.shards.data.lavalink.pause(ctx.guild_id)
    await ctx.shards.data.lavalink.set_pause(ctx.guild_id, True)
    embed = Embed(title="⏸️ Playback Paused", color=0xFF0000)
    await ctx.respond(embed=embed)


@component.with_slash_command
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
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.queue:
        return await ctx.respond("There are no tracks in the queue!")

    for song in node.queue:
        song_queue += [
            f"[{song.track.info.title}]({song.track.info.uri}) [<@{song.requester}>]"
        ]

    fields = []
    counter = 1
    if not len(song_queue[1:]) > 0:
        return await ctx.respond(
            f"No tracks in the queue.\n**Now Playing** : [{node.now_playing.track.info.title}]({node.now_playing.track.info.uri})"
        )
    for index, track in enumerate(_chunk(song_queue[1:], 8)):
        string = """"""
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
            name="Now Playing",
            value=f"[{node.now_playing.track.info.title}]({node.now_playing.track.info.uri}) [<@{node.now_playing.requester}>]",
        )
        temp.append(hikari.UNDEFINED)
        temp.append(embed)
        fields.append(temp)

    await paginate(ctx, fields, 180)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("resume", "Resume the song that is paused")
@check_voice_state
async def resume(ctx: tanjun.abc.Context) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond("No tracks are currently playing!")

    if node.is_paused:
        await ctx.shards.data.lavalink.resume(ctx.guild_id)
        embed = Embed(description=f"🎵 Resumed the Playback!", color=0x00FF00)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("It's already resumed. 😡")


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.with_int_slash_option("volume", "Volume to be set (Between 0 and 100)")
@tanjun.as_slash_command("volume", "Increase/Decrease the volume")
async def volume(ctx: tanjun.abc.Context, volume: int) -> None:
    await check_voice_state(ctx)
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond("Nothing is being played at the moment")

    if 0 < volume <= 100:
        await ctx.shards.data.lavalink.volume(ctx.guild_id, volume)
        embed = Embed(description=f"⏯️ Set the Volume to {volume}", color=0x00FF00)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("Volume should be between 0 and 100")


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("skip", "Skips the current song")
@check_voice_state
async def skip(ctx: tanjun.abc.Context) -> None:

    skip = await ctx.shards.data.lavalink.skip(ctx.guild_id)
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not skip:
        return await ctx.respond("Nothing to skip")

    if not node.queue and not node.now_playing:
        await ctx.shards.data.lavalink.stop(ctx.guild_id)

    em = hikari.Embed(
        title="⏭️ Skipped",
        description=f"[{skip.track.info.title}]({skip.track.info.uri})",
    )

    await ctx.respond(embed=em)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("shuffle", "Shuffle the current queue")
@check_voice_state
async def shuffle(ctx: tanjun.abc.Context) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)
    if not len(node.queue) > 1:
        return ctx.respond("Only one song in the queue!")

    queue = node.queue[1:]
    random.shuffle(queue)

    queue.insert(0, node.queue[0])

    node.queue = queue
    await ctx.shards.data.lavalink.set_guild_node(ctx.guild_id, node)

    embed = hikari.Embed(title="🔀 Shuffled Queue", color=0x00FF00)
    await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("lyrics", "Get lyrics of Currently playing song")
async def lyrics(ctx: tanjun.abc.Context) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)
    if not node.now_playing:
        return await ctx.respond("There's nothing playing at the moment!")
    song_name = node.now_playing.track.info.title
    async with aiohttp.request(
        "GET", f"https://some-random-api.ml/lyrics?title={song_name}", headers={}
    ) as r:
        if not 200 <= r.status <= 299:
            raise tanjun.CommandError("No Lyrics found.")
        data = await r.json()

    lyrics = str(data["lyrics"])
    iterator = lyrics.splitlines()

    fields = (
        (
            hikari.UNDEFINED,
            hikari.Embed(
                description="\n".join(lyric),
                color=0x00FF00,
                timestamp=datetime.now().astimezone(),
            )
            .set_footer(text=f"Page {index+1}")
            .set_author(name=f"{song_name}", url=f"{node.now_playing.track.info.uri}"),
        )
        for index, lyric in enumerate(_chunk(iterator, 30))
    )
    await paginate(ctx, fields, 180)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.with_int_slash_option("new_index", "New Index the song is moved to")
@tanjun.with_int_slash_option("old_index", "Song to move")
@tanjun.as_slash_command("movesong", "Move a song to a specific index")
@check_voice_state
async def movesong(ctx: tanjun.abc.Context, old_index: int, new_index: int) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)
    if not len(node.queue) >= 1:
        return ctx.respond("Only one song in the queue!")
    queue = node.queue
    song_to_be_moved = queue[old_index]
    try:
        queue.pop(old_index)
        queue.insert(new_index, song_to_be_moved)
    except IndexError:
        raise tanjun.CommandError("No such song in the queue.")

    node.queue = queue
    await ctx.shards.data.lavalink.set_guild_node(ctx.guild_id, node)
    embed = hikari.Embed(
        title=f"Moved `{song_to_be_moved.track.info.title}` to Position `{new_index}`",
        color=0x00FF00,
    )
    await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.with_int_slash_option("index", "Index of the Song to be removed")
@tanjun.as_slash_command("removesong", "Remove a song at a specific index")
@check_voice_state
async def removesong(ctx: tanjun.abc.Context, index: int) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)
    if not node.queue:
        return await ctx.respond("No songs in the queue.")
    queue: list = node.queue
    song_to_be_removed = queue[index]
    try:
        queue.pop(index)
    except IndexError:
        raise tanjun.CommandError("No such song in the queue.")

    node.queue = queue
    await ctx.shards.data.lavalink.set_guild_node(ctx.guild_id, node)
    embed = hikari.Embed(
        title=f"Removed `{song_to_be_removed.track.info.title}` from the queue."
    )
    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
