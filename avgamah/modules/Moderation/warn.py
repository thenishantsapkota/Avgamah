from datetime import datetime

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW
from avgamah.utils.time import pretty_datetime
from models import WarningsModel

from . import permissions, warning_count

warn_component = tanjun.Component()


@warn_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_MESSAGES
    | hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("reason", "Reason to warn the member")
@tanjun.with_member_slash_option("member", "Member to warn")
@tanjun.as_slash_command("warn", "Warn a user in the server")
async def warn_command(
    ctx: tanjun.abc.Context, member: hikari.Member, reason: str
) -> None:
    author = ctx.member
    guild = ctx.get_guild()
    await permissions.staff_role_check(ctx, guild)
    log_channel = await permissions.log_channel_check(ctx, guild)
    await permissions.check_higher_role(author, member)
    model = await WarningsModel.create(
        guild_id=ctx.guild_id,
        member_id=member.id,
        reason=reason,
        author_name=author,
        date=pretty_datetime(datetime.now()),
    )
    await model.save()
    embed = hikari.Embed(
        color=0xFFA500,
        timestamp=datetime.now().astimezone(),
        description=f"⚠️ **Warned {member}** [ ID {member.id}]\n📄**Reason:**{reason}",
    )
    embed.set_thumbnail(member.avatar_url)
    embed.set_author(name=f"{author} [ ID {author.id}]", icon=author.avatar_url)
    await log_channel.send(embed=embed)
    await ctx.respond(f"⚠️ ** Warned `{member}`**", component=DELETE_ROW)
    try:
        await member.send(f"⚠️ Warned in {guild.name}\n📄Reason: {reason}")

    except hikari.ForbiddenError:
        pass

    await warning_count(ctx, member)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(warn_component.copy())
