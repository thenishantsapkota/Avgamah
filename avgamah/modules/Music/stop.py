import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import check_voice_state, fetch_lavalink

stop_component = tanjun.Component()


@stop_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("stop", "Stop the playback")
@check_voice_state
async def stop(ctx: tanjun.abc.Context) -> None:
    lavalink = fetch_lavalink(ctx)
    await lavalink.stop(ctx.guild_id)

    embed = hikari.Embed(
        title="⏹️ Playback Stopped!",
        color=0xFF0000,
    )
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(stop_component.copy())
