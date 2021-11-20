from datetime import datetime

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

serverinfo_component = tanjun.Component()


@serverinfo_component.with_slash_command
@tanjun.as_slash_command("serverinfo", "Get info about the server.")
async def serverinfo_command(ctx: tanjun.abc.Context) -> None:
    guild = await ctx.fetch_guild()
    embed = hikari.Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
    )
    embed.set_author(name=f"Serverinfo of {guild}", icon=guild.icon_url)
    fields = [
        ("ID", ctx.guild_id, True),
        ("Owner", f"<@{guild.owner_id}>", True),
        ("Member Count", len(guild.get_members()), True),
        (
            "Server Creation",
            f"<t:{guild.created_at.timestamp():.0f}:F> • <t:{guild.created_at.timestamp():.0f}:R>",
            True,
        ),
        ("Total Channels", len(guild.get_channels()), True),
        ("Boost Count", guild.premium_subscription_count, True),
        (
            "Premium Tier",
            str(guild.premium_tier).replace("_", " ").title(),
            True,
        ),
        ("Role Count", len(guild.get_roles()), True),
        (
            "Vanity URL",
            f"https://discord.gg/{guild.vanity_url_code}"
            if guild.vanity_url_code
            else "None",
            True,
        ),
    ]
    embed.set_thumbnail(guild.icon_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon=ctx.author.avatar_url)

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    if guild.features:
        embed.add_field(
            name="Features",
            value="\n".join(
                "• " + feature.replace("_", " ").title() for feature in guild.features
            ),
        )

    await ctx.respond(embed=embed, component=DELETE_ROW)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(serverinfo_component.copy())
