import hikari
import tanjun

from itsnp.core.client import Client

from . import _leave, check_voice_state

leave_component = tanjun.Component()


@leave_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("leave", "Leave the voice channel")
@check_voice_state
async def leave(ctx: tanjun.abc.Context) -> None:
    await _leave(ctx)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(leave_component.copy())
