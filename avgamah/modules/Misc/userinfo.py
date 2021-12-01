from datetime import datetime

import hikari
import tanjun

from avgamah.core.client import Client

userinfo_component = tanjun.Component()


@userinfo_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_member_slash_option("member", "Choose a member", default=False)
@tanjun.as_slash_command(
    "userinfo", "Get info of a user in a guild", default_to_ephemeral=True
)
async def userinfo_command(ctx: tanjun.abc.Context, member: hikari.Member) -> None:
    member = member or ctx.member
    created_at = int(member.created_at.timestamp())
    joined_at = int(member.joined_at.timestamp())

    roles = (await member.fetch_roles())[1:]
    perms = hikari.Permissions.NONE

    for r in roles:
        perms |= r.permissions

    permissions = str(perms).split("|")

    status = (
        member.get_presence().visible_status if member.get_presence() else "Offline"
    )

    embed = hikari.Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
    )
    fields = [
        ("ID", member.id, True),
        ("Joined on", f"<t:{joined_at}:F> • <t:{joined_at}:R>", False),
        ("Created on", f"<t:{created_at}:F> • <t:{created_at}:R>", False),
        ("Nickname", member.nickname if member.nickname else "None", True),
        ("Status", status.title(), True),
        (
            "Permissions",
            ",".join(perm.replace("_", " ").title() for perm in permissions),
            False,
        ),
        ("Roles", ",".join(r.mention for r in roles), False),
    ]

    if member.is_bot:
        embed.description = "The user I am looking at is a Bot, just like me.<a:peeporgb:841033889798946856>"

    embed.set_author(name=f"User Info of - {member}")
    embed.set_thumbnail(member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon=ctx.author.avatar_url)
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(userinfo_component.copy())
