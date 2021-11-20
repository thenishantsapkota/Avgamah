import re
from math import tan

import hikari
import lavasnek_rs
import tanjun

from avgamah.utils.buttons import DELETE_ROW

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
        return await ctx.respond(
            "Connect to a voice channel to continue!", component=DELETE_ROW
        )

    channel_id = voice_state[0].channel_id

    try:
        connection_info = await lavalink.join(ctx.guild_id, channel_id)

    except TimeoutError:
        return await ctx.respond(
            "I cannot connect to your voice channel!", component=DELETE_ROW
        )

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
