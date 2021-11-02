import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW

from . import check_voice_state

move_song_component = tanjun.Component()


@move_song_component.with_slash_command
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
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(move_song_component.copy())
