from datetime import datetime, timedelta
from platform import python_version
from time import time

import hikari
import tanjun
from hikari import ButtonStyle
from hikari import __version__ as hikari_version
from psutil import Process, virtual_memory
from tanjun import __version__ as tanjun_version

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW
from avgamah.utils.time import pretty_timedelta

botinfo_component = tanjun.Component()


@botinfo_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command("botinfo", "View Bot's info")
async def botinfo_command(ctx: tanjun.abc.Context) -> None:
    proc = Process()
    bot = await ctx.rest.fetch_my_user()
    with proc.oneshot():
        uptime = timedelta(seconds=time() - proc.create_time())
        pretty_uptime = pretty_timedelta(uptime)
        cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
        pretty_cpu_time = pretty_timedelta(cpu_time)
        mem_total = virtual_memory().total / (1024 ** 2)
        mem_of_total = proc.memory_percent()
        mem_usage = mem_total * (mem_of_total / 100)

    embed = hikari.Embed(
        title=f"{await ctx.rest.fetch_my_user()}'s Information",
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
    )
    embed.set_thumbnail(bot.avatar_url)
    fields = [
        ("Language", "Python", True),
        ("Python Version", python_version(), True),
        ("Bot Version", "1.0.0", True),
        ("Library", f"hikari-py v{hikari_version}", True),
        ("Command Handler", f"hikari-tanjun v{tanjun_version}", True),
        ("Uptime", pretty_uptime, True),
        ("CPU Time", pretty_cpu_time, True),
        (
            "Memory Usage",
            f"{mem_usage:,.0f} MiB /{mem_total:,.0f} MiB ({((mem_usage/mem_total) * 100):,.1f} %)",
            False,
        ),
        ("Prefix", "/", True),
        (
            "Total Guild Channels",
            len(ctx.cache.get_guild_channels_view()),
            True,
        ),
        (
            "Total Members",
            sum(len(record) for record in ctx.cache.get_members_view().values()),
            True,
        ),
        ("Total Guilds", len(ctx.cache.get_available_guilds_view()), True),
        ("Owner <:crown:879222224438059049>", "<@852617608309112882>", True),
    ]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    button = (
        ctx.rest.build_action_row()
        .add_button(ButtonStyle.LINK, "https://discord.gg/remVxztXYs")
        .set_label("Support Server")
        .add_to_container()
        .add_button(ButtonStyle.LINK, "https://github.com/thenishantsapkota/Hikari-Bot")
        .set_label("Source")
        .add_to_container()
        .add_button(
            ButtonStyle.LINK,
            f"https://discord.com/api/oauth2/authorize?client_id={bot.id}&permissions=8&scope=bot%20applications.commands",
        )
        .set_label("Invite Me")
        .add_to_container()
    )

    await ctx.respond(embed=embed, components=[button, DELETE_ROW])


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(botinfo_component.copy())
