import hikari
import tanjun

from itsnp.core.client import Client

from . import check_voice_state

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
    node = await ctx.shards.data.lavalink.get_guild_node(ctx.guild_id)

    if not node or not node.now_playing:
        return await ctx.respond("No tracks are currently playing!")

    if node.is_paused:
        await ctx.shards.data.lavalink.resume(ctx.guild_id)
        embed = hikari.Embed(description=f"🎵 Resumed the Playback!", color=0x00FF00)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("It's already resumed. 😡")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(resume_component.copy())
