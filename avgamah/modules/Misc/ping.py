import random

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

ping_component = tanjun.Component()


@ping_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command("ping", "Return bot ping.")
async def ping_command(ctx: tanjun.abc.Context) -> None:
    heartbeat_latency = (
        ctx.shards.heartbeat_latency * 1_000 if ctx.shards else float("NAN")
    )
    await ctx.respond("Pinging the API.....")
    embed = hikari.Embed(
        description=f"I pinged the API and got these results.\n**Gateway:** {heartbeat_latency:.0f}ms",
        color=0xF1C40F,
    )
    embed.set_author(name="Ping")
    await ctx.edit_last_response("", embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(ping_component.copy())
