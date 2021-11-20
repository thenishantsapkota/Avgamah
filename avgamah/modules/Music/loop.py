import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import check_voice_state

loop_component = tanjun.Component()


@loop_component.with_slash_command
@tanjun.with_str_slash_option(
    "choice",
    "Choose what to loop",
    choices=(
        "track",
        "queue",
    ),
)
@tanjun.as_slash_command("loop", "Loop the currently playing song or the queue once")
@check_voice_state
async def loop(ctx: tanjun.abc.Context, choice: str) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)
    if not node.queue:
        raise tanjun.CommandError("No Tracks in the Queue.")

    queue: list = node.queue
    if choice == "track":
        now_playing = queue[0]
        queue.insert(1, now_playing)
        node.queue = queue
        await ctx.shards.data.lavalink.set_guild_node(ctx.guild_id, node)
        await ctx.respond("Looping the currently playing track.", component=DELETE_ROW)
    elif choice == "queue":
        queue.extend(queue)
        node.queue = queue
        await ctx.shards.data.lavalink.set_guild_node(ctx.guild_id, node)
        await ctx.respond("Looping the queue again.", component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(loop_component.copy())
