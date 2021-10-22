import asyncio
from datetime import datetime
from typing import Optional

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.time import *
from models import MuteModel

from . import permissions, unmute_handler

unmute_component = tanjun.Component()


@unmute_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_MESSAGES
    | hikari.Permissions.MANAGE_ROLES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("reason", "Reason to unmute the user", default=False)
@tanjun.with_member_slash_option("member", "Member to mutes")
@tanjun.as_slash_command("unmute", "Unmute a member from the server.")
async def unmute_command(
    ctx: tanjun.abc.Context,
    member: hikari.Member,
    *,
    reason: Optional[str] = "No reason provided.",
) -> None:
    await permissions.mod_role_check(ctx, ctx.get_guild())
    await unmute_handler(ctx, member, reason=reason)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(unmute_component.copy())
