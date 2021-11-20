import random

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import check_voice_state, fetch_lavalink

shuffle_component = tanjun.Component()


@shuffle_component.with_slash_command
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
    lavalink = fetch_lavalink(ctx)
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not len(node.queue) > 1:
        return ctx.respond("Only one song in the queue!")

    queue = node.queue[1:]
    random.shuffle(queue)

    queue.insert(0, node.queue[0])

    node.queue = queue
    await lavalink.set_guild_node(ctx.guild_id, node)

    embed = hikari.Embed(title="🔀 Shuffled Queue", color=0x00FF00)
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(shuffle_component.copy())
