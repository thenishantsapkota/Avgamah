import re
from math import tan

import hikari
import tanjun

from avgamah.core import Client

from . import TIME_REGEX, check_voice_state, fetch_lavalink

seek_component = tanjun.Component()


@seek_component.with_slash_command
@tanjun.with_str_slash_option("position", "Position to seek to Eg - 1m2s")
@tanjun.as_slash_command("seek", "Seek the currently playing track")
@check_voice_state
async def seek(ctx: tanjun.abc.Context, position: str) -> None:
    lavalink = fetch_lavalink(ctx)

    node = await lavalink.get_guild_node(ctx.guild_id)

    if not node.queue:
        raise tanjun.CommandError("The queue is currently empty.")

    if not (match := re.match(TIME_REGEX, position)):
        raise tanjun.CommandError("Invalid Time String")

    if match.group(3):
        secs = (int(match.group(1)) * 60) + (int(match.group(3)))
    else:
        secs = int(match.group(1))

    await lavalink.jump_to_time_secs(ctx.guild_id, secs)

    await ctx.respond(
        embed=hikari.Embed(description=f"⏩ Seeked to {position}.", color=0x00FF00)
    )


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(seek_component.copy())
