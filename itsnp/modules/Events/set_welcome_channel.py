from datetime import datetime

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW
from models import MemberJoinModel

from . import permissions

set_welcome_component = tanjun.Component()


@set_welcome_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_channel_slash_option(
    "channel", "The channel you want to set as Welcome Channel"
)
@tanjun.as_slash_command(
    "setwelcomechannel",
    "Set a Welcome Channel for the guild",
    default_to_ephemeral=True,
)
async def set_welcome_channel(
    ctx: tanjun.abc.Context, channel: hikari.GuildTextChannel
) -> None:
    await permissions.admin_role_check(ctx, ctx.get_guild())
    model, _ = await MemberJoinModel.get_or_create(
        guild_id=ctx.guild_id, channel_id=channel.id
    )
    await model.save()
    embed = hikari.Embed(
        title="Configuration",
        description=f"The Welcome Channel for this guild has been set to {channel}",
        timestamp=datetime.now().astimezone(),
        color=0x00FF00,
    )
    embed.set_thumbnail(ctx.get_guild().icon_url)
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(set_welcome_component.copy())
