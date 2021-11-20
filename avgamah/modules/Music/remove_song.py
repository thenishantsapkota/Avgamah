import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import check_voice_state

remove_song_component = tanjun.Component()


@remove_song_component.with_slash_command
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
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(remove_song_component.copy())
