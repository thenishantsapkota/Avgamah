from datetime import datetime

import hikari
import tanjun

from itsnp.core.client import Client
from models import ModerationRoles

from . import role_group

list_component = tanjun.Component()


@role_group.with_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command("list", "List moderation roles for the server")
async def list_command(ctx: tanjun.abc.Context) -> None:
    guild = ctx.get_guild()
    model = await ModerationRoles.get_or_none(guild_id=guild.id)
    if model is None:
        return await ctx.respond("No data found.")

    embed = hikari.Embed(
        color=hikari.Color(0x00FF00),
        timestamp=datetime.now().astimezone(),
    )

    fields = [
        ("Admin Role", f"<@&{model.admin_role}>", True),
        ("Moderator Role", f"<@&{model.mod_role}>", True),
        ("Staff Role", f"<@&{model.staff_role}>", True),
    ]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_author(name=f"Staff Roles for {guild.name}", icon=guild.icon_url)
    embed.set_footer(text=f"Invoked by {ctx.author}")
    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(list_component.copy())
