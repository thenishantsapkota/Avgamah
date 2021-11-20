import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import check_voice_state, fetch_lavalink

volume_component = tanjun.Component()


@volume_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.with_int_slash_option("volume", "Volume to be set (Between 0 and 100)")
@tanjun.as_slash_command("volume", "Increase/Decrease the volume")
@check_voice_state
async def volume(ctx: tanjun.abc.Context, volume: int) -> None:
    lavalink = fetch_lavalink(ctx)
    node = await lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond(
            "Nothing is being played at the moment", component=DELETE_ROW
        )

    if 0 < volume <= 100:
        await lavalink.volume(ctx.guild_id, volume)
        embed = hikari.Embed(
            description=f"⏯️ Set the Volume to {volume}", color=0x00FF00
        )
        await ctx.respond(embed=embed, component=DELETE_ROW)
    else:
        await ctx.respond("Volume should be between 0 and 100", component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(volume_component.copy())
