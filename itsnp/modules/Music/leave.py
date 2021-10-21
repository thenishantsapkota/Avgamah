import hikari
import tanjun

from itsnp.core.client import Client

from . import check_voice_state

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
    await ctx.shards.data.lavalink.destroy(ctx.guild_id)
    await ctx.shards.data.lavalink.stop(ctx.guild_id)
    await ctx.shards.data.lavalink.leave(ctx.guild_id)
    await ctx.shards.data.lavalink.remove_guild_node(ctx.guild_id)
    await ctx.shards.data.lavalink.remove_guild_from_loops(ctx.guild_id)

    embed = hikari.Embed(
        description=f"I left the voice channel!",
        color=0xFF0000,
    )
    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(leave_component.copy())
