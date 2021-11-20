from datetime import datetime

import aiohttp
import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.pagination import paginate
from avgamah.utils.utilities import _chunk

lyrics_component = tanjun.Component()


@lyrics_component.with_slash_command
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
        "GET",
        f"https://some-random-api.ml/lyrics?title={song_name}",
        headers={},
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
        for index, lyric in enumerate(_chunk(iterator, 20))
    )
    await paginate(ctx, fields, 180)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(lyrics_component.copy())
