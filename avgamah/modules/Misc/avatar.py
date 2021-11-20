from datetime import datetime

import hikari
import tanjun

from avgamah.core.client import Client

avatar_component = tanjun.Component()


@avatar_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_member_slash_option("member", "Get member.")
@tanjun.as_slash_command("avatar", "View a member's avatar", default_to_ephemeral=True)
async def avatar_command(
    ctx: tanjun.abc.Context, member: hikari.InteractionMember
) -> None:
    embed = hikari.Embed(
        title=f"Avatar of {member}",
        timestamp=datetime.now().astimezone(),
        color=0xF1C40F,
    )
    embed.set_image(member.avatar_url)
    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(avatar_component.copy())
