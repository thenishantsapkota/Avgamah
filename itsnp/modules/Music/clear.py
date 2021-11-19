import hikari
import tanjun

from itsnp.core import Client
from itsnp.utils.buttons import DELETE_ROW

from . import fetch_lavalink

clear_component = tanjun.Component()


@clear_component.with_slash_command
@tanjun.as_slash_command("clear", "Clear the queue.")
async def clear_queue(ctx: tanjun.abc.Context) -> None:
    lavalink = fetch_lavalink(ctx)
    node = await lavalink.get_guild_node(ctx.guild_id)

    if not node.queue:
        raise tanjun.CommandError("No Tracks in the queue.")

    queue = node.queue[1:]

    queue.clear()
    queue.insert(0, node.queue[0])
    node.queue = queue

    await lavalink.set_guild_node(ctx.guild_id, node)
    await ctx.respond(
        embed=hikari.Embed(
            description="Cleared the queue. :ok_hand:",
            color=0x00FF00,
        ),
        component=DELETE_ROW,
    )


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(clear_component.copy())
