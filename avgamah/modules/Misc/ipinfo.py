from datetime import datetime

import aiohttp
import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import create_source_button

ipinfo_component = tanjun.Component()


@ipinfo_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("ip", "IP Address you want to lookup")
@tanjun.as_slash_command(
    "ipinfo", "Get info about an IP Address", default_to_ephemeral=True
)
async def ipinfo_command(ctx: tanjun.abc.Context, ip: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://ip-api.com/json/{ip}") as resp:
            ip_info = await resp.json()

    if ip.startswith("127") or ip.startswith("192.168"):
        return await ctx.respond(
            "You cannot lookup Localhost"
            if ip.startswith("127")
            else "You provided Local IP Address"
        )

    embed = hikari.Embed(
        title=f"Info of IP {ip}",
        color=hikari.Color(0x00FF00),
        timestamp=datetime.now().astimezone(),
    )

    fields = [
        ("IP", ip_info["query"], True),
        ("Country", ip_info["country"], True),
        ("Region", ip_info["regionName"].title(), True),
        ("City", ip_info["city"], True),
        ("Latitude/Longitude", f"{ip_info['lat']}°/{ip_info['lon']}°", True),
        ("ISP", ip_info["isp"], True),
    ]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    button = create_source_button(ctx, "http://ip-api.com/")

    await ctx.respond(embed=embed, component=button)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(ipinfo_component.copy())
