import hikari
import tanjun

from itsnp.core.client import Client

from . import check_voice_state

pause_component = tanjun.Component()


@pause_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("pause", "Pause the current song being played")
@check_voice_state
async def pause(ctx: tanjun.abc.Context) -> None:
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond("There are no tracks currently playing!")

    if node.is_paused:
        return await ctx.respond("Playback is already paused!")

    await ctx.shards.data.lavalink.pause(ctx.guild_id)
    await ctx.shards.data.lavalink.set_pause(ctx.guild_id, True)
    embed = hikari.Embed(title="⏸️ Playback Paused", color=0xFF0000)
    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(pause_component.copy())
