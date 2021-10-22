from datetime import datetime

import hikari
import tanjun

from itsnp.core.client import Client
from models import ModerationRoles

from . import role_group

mod_role_component = tanjun.Component()


@role_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_role_slash_option("role", "Role or role id of mod role")
@tanjun.as_slash_command("mod", "Set mod role for the server.")
async def mod_role_command(ctx: tanjun.abc.Context, role: hikari.Role) -> None:
    guild = ctx.get_guild()
    model, _ = await ModerationRoles.get_or_create(guild_id=ctx.guild_id)
    model.mod_role = role.id
    await model.save()
    embed = hikari.Embed(
        title="Moderator Role",
        description=f"The mod role  for {guild.name} has been set to {role.mention}",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0x00FF00),
    )
    await ctx.respond(embed=embed)


mod_role_component.add_slash_command(role_group)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(mod_role_component.copy())
