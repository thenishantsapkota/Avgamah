import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

from . import check_voice_state, fetch_lavalink

resume_component = tanjun.Component()


@resume_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
    | hikari.Permissions.CONNECT
    | hikari.Permissions.SPEAK
)
@tanjun.as_slash_command("resume", "Resume the song that is paused")
@check_voice_state
async def resume(ctx: tanjun.abc.Context) -> None:
    lavalink = fetch_lavalink(ctx)
    node = await lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond(
            "No tracks are currently playing!", component=DELETE_ROW
        )

    if node.is_paused:
        await lavalink.resume(ctx.guild_id)
        embed = hikari.Embed(description="🎵 Resumed the Playback!", color=0x00FF00)
        await ctx.respond(embed=embed, component=DELETE_ROW)
    else:
        await ctx.respond("It's already resumed. 😡", component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(resume_component.copy())
