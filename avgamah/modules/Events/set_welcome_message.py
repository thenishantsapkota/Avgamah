import typing as t
from datetime import datetime

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW
from models import MemberJoinModel

from . import permissions

set_message_component = tanjun.Component()


@set_message_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option(
    "message", "The Welcome message for the server", default=None
)
@tanjun.as_slash_command(
    "setwelcomemessage",
    "Set welcome message for the guild.",
    default_to_ephemeral=True,
)
async def set_welcome_message(
    ctx: tanjun.abc.Context, message: t.Optional[str]
) -> None:
    await permissions.admin_role_check(ctx, ctx.get_guild())
    default = "Enjoy your stay here"
    welcome = await MemberJoinModel.get_or_none(guild_id=ctx.guild_id)
    welcome.welcome_message = message
    await welcome.save()
    embed = hikari.Embed(
        title="Configuration",
        description=f"The welcome message for {ctx.get_guild()} has been set to `{message if message else default}`",
        timestamp=datetime.now().astimezone(),
        color=0x00FF00,
    )
    embed.set_thumbnail(ctx.get_guild().icon_url)
    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(set_message_component.copy())
