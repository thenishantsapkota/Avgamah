import typing as t
from datetime import datetime, timedelta

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW
from itsnp.utils.time import TimeConverter, pretty_timedelta

slowmode_component = tanjun.Component()


@slowmode_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_CHANNELS
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.READ_MESSAGE_HISTORY
    | hikari.Permissions.SEND_MESSAGES
)
@tanjun.with_str_slash_option("time", "Slowmode Time (h/m/s)")
@tanjun.with_channel_slash_option(
    "channel",
    "Channel you want slowmode invoked in(TextChannels)",
    default=None,
)
@tanjun.as_slash_command("slowmode", "Invoke slowmode in the selected channel")
async def slowmode(
    ctx: tanjun.abc.Context,
    channel: t.Optional[hikari.InteractionChannel],
    time: str,
) -> None:
    if not channel:
        channel = ctx.get_channel()

    time_seconds = await TimeConverter.convert(TimeConverter, ctx, time)
    await ctx.rest.edit_channel(channel, rate_limit_per_user=time_seconds)
    embed = hikari.Embed(
        title="Slowmode Edited",
        description=f"The slowmode of `{channel}` has been set to `{pretty_timedelta(timedelta(seconds=time_seconds)) if time_seconds else 'None'}`",
        timestamp=datetime.now().astimezone(),
        color=0x00FF00,
    )
    embed.set_footer(text=f"Invoked by {ctx.author}")

    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(slowmode_component.copy())
