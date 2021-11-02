import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW

from . import check_voice_state

skip_component = tanjun.Component()


@skip_component.with_slash_command
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

    await ctx.respond(embed=em, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(skip_component.copy())
