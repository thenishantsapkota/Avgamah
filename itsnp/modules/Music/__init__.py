import re

import hikari
import tanjun

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


async def _leave(ctx: tanjun.abc.Context):
    await ctx.shards.data.lavalink.destroy(ctx.guild_id)
    await ctx.shards.data.lavalink.stop(ctx.guild_id)
    await ctx.shards.data.lavalink.leave(ctx.guild_id)
    await ctx.shards.data.lavalink.remove_guild_node(ctx.guild_id)
    await ctx.shards.data.lavalink.remove_guild_from_loops(ctx.guild_id)

    embed = hikari.Embed(
        description="I left the voice channel!",
        color=0xFF0000,
    )
    await ctx.respond(embed=embed)
