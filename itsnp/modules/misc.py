from datetime import datetime, timedelta
import random

import hikari
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import ButtonStyle
import tanjun
from hikari import Embed
from time import time

from itsnp.core.client import Client
from itsnp.utils.time import *
from platform import python_version
from hikari import __version__ as hikari_version
from tanjun import __version__ as tanjun_version
from itsnp import __version__ as bot_version
from psutil import Process, virtual_memory

component = tanjun.Component()

LINKS_DICT = {
    "Facebook Group": "https://www.facebook.com/groups/techforimpact",
    "Donate Us": "https://tiny.cc/itsnpdonate",
    "Facebook": "https://tiny.cc/itsnpfb",
    "Instagram": "https://tiny.cc/itsnpig",
    "Discord": "https://tiny.cc/itsnpdiscord",
    "Twitter": "https://tiny.cc/itsnptwitter",
    "Youtube": "https://tiny.cc/itsnpyt",
    "Workshop": "https://tiny.cc/itsnpworkshop",
    "Github": "https://github.com/itsnporg",
    "Live": "https://tiny.cc/itsnplive",
}

PLATFORM = list(LINKS_DICT.keys())


@component.with_slash_command
@tanjun.as_slash_command("hello", "Greet the user with hello.")
async def hello_command(ctx: tanjun.abc.Context) -> None:
    greeting = random.choice(("Hello", "Hi", "Hey"))
    await ctx.respond(f"{greeting} {ctx.member.mention}!", user_mentions=True)


@component.with_slash_command
@tanjun.as_slash_command("ping", "Return bot ping.")
async def ping_command(ctx: tanjun.abc.Context) -> None:
    heartbeat_latency = (
        ctx.shards.heartbeat_latency * 1_000 if ctx.shards else float("NAN")
    )
    await ctx.respond("Pinging the API.....")
    embed = Embed(
        description=f"I pinged the API and got these results.\n**Gateway:** {heartbeat_latency:.0f}ms",
        color=0xF1C40F,
    )
    embed.set_author(name="Ping")
    await ctx.edit_last_response("", embed=embed)


@component.with_slash_command
@tanjun.with_str_slash_option(
    "platform", "The link to show", choices=(l.lower() for l in PLATFORM)
)
@tanjun.as_slash_command("link", "Show different ITSNP link")
async def link_command(ctx: tanjun.abc.Context, platform: str) -> None:
    button = (
        ctx.rest.build_action_row()
        .add_button(ButtonStyle.LINK, LINKS_DICT[platform.title()])
        .set_label(platform.title())
        .add_to_container()
    )
    await ctx.respond(f"**{platform.title()}**", component=button)


@component.with_slash_command
@tanjun.with_member_slash_option("member", "Get member.")
@tanjun.as_slash_command("avatar", "View a member's avatar", default_to_ephemeral=True)
async def avatar_command(
    ctx: tanjun.abc.Context, member: hikari.InteractionMember
) -> None:
    embed = Embed(
        title=f"Avatar of {member}",
        timestamp=datetime.now().astimezone(),
        color=0xF1C40F,
    )
    embed.set_image(member.avatar_url)
    await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.as_slash_command("links", "Get all ITSNP Links")
async def links_command(ctx: tanjun.abc.Context) -> None:
    rows = []
    for i in range(0, len(PLATFORM), 2):
        row = ctx.rest.build_action_row()
        for link in PLATFORM[i : i + 2]:
            (
                row.add_button(ButtonStyle.LINK, LINKS_DICT[link])
                .set_label(link)
                .add_to_container()
            )
        rows.append(row)
    await ctx.respond("**Here are all the ITSNP Links**", components=rows)


@component.with_slash_command
@tanjun.as_slash_command("serverinfo", "Get info about the server.")
async def serverinfo_command(ctx: tanjun.abc.Context) -> None:
    guild = await ctx.fetch_guild()
    embed = Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
    )
    embed.set_author(name=f"Serverinfo of {guild}", icon=guild.icon_url)
    fields = [
        ("ID", ctx.guild_id, True),
        ("Owner", f"<@{guild.owner_id}>", True),
        ("Member Count", len(guild.get_members()), True),
        ("Server Creation", f"<t:{guild.created_at.timestamp():.0f}:F>", True),
        ("Total Channels", len(guild.get_channels()), True),
        ("Boost Count", guild.premium_subscription_count, True),
        ("Premium Tier", str(guild.premium_tier).replace("_", " ").title(), True),
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

    await ctx.respond(embed=embed)


@component.with_slash_command
@tanjun.with_member_slash_option("member", "Choose a member")
@tanjun.as_slash_command(
    "userinfo", "Get info of a user in a guild", default_to_ephemeral=True
)
async def userinfo_command(ctx: tanjun.abc.Context, member: hikari.Member) -> None:
    created_at = int(member.created_at.timestamp())
    joined_at = int(member.joined_at.timestamp())

    roles = (await member.fetch_roles())[1:]
    status = member.get_presence().visible_status if member.get_presence() else "Offline"

    embed = Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
    )
    fields = [
        ("ID", member.id, True),
        ("Joined on", f"<t:{joined_at}:F>", True),
        ("Created on", f"<t:{created_at}:F>", True),
        ("Nickname", member.nickname if member.nickname else "None", True),
        ("Status", status.title() , True),
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

@component.with_slash_command
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
    
    embed = Embed(
        title = f"{await ctx.rest.fetch_my_user()}'s Information",
        color = 0xF1C40F,
        timestamp = datetime.now().astimezone(),
        description=f"```Language : Python\nPython Version : {python_version()}\nBot Version : {bot_version}\nLibrary : hikari.py\nCommand Handler : hikari-tanjun\nHikari Version : {hikari_version}\nTanjun Version : {tanjun_version}\nUptime : {pretty_uptime}\nCPU Time : {pretty_cpu_time}\nMemory Usage : {mem_usage:,.3f} MiB /{mem_total:,.0f} MiB\nPrefix : /\nClient ID : {bot.id}```"
    )
    embed.set_thumbnail(bot.avatar_url)
    fields = [("Owner <:crown:879222224438059049>", f"<@852617608309112882>")]
    for name, value in fields:
        embed.add_field(name=name, value=value)
    
    button = (
        ctx.rest.build_action_row()
        .add_button(ButtonStyle.LINK, "https://discord.gg/5Tf468hhJy")
        .set_label("Support Server")
        .add_to_container()
        .add_button(ButtonStyle.LINK, "https://github.com/thenishantsapkota/Hikari-Bot")
        .set_label("Source")
        .add_to_container()
    )

    await ctx.respond(embed=embed, component= button)

        

@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
