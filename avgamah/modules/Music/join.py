import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import _join

join_component = tanjun.Component()


@join_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("join", "Join a voice channel of a guild")
async def join(ctx: tanjun.abc.Context) -> None:
    channel_id = await _join(ctx)

    if channel_id:
        embed = hikari.Embed(description=f"Joined <#{channel_id}>", color=0x00FF00)
        await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(join_component.copy())
