import os
import random
from datetime import datetime, timedelta
from platform import python_version
from time import time

import aiohttp
import hikari
import tanjun
from hikari import Embed
from hikari import __version__ as hikari_version
from hikari.messages import ButtonStyle
from lightbulb import __version__ as lighbulb_version
from psutil import Process, virtual_memory
from tanjun import __version__ as tanjun_version
from tanjun import components

from itsnp import __version__ as bot_version
from itsnp.core.client import Client
from itsnp.utils.buttons import create_source_button
from itsnp.utils.time import *

component = tanjun.Component()

LINKS_DICT = {
    "Facebook Group": "https://www.facebook.com/groups/techforimpact",
    "Facebook": "https://tiny.cc/itsnpfb",
    "Instagram": "https://tiny.cc/itsnpig",
    "Discord": "https://tiny.cc/itsnpdiscord",
    "Twitter": "https://tiny.cc/itsnptwitter",
    "Youtube": "https://tiny.cc/itsnpyt",
    "Workshop": "https://tiny.cc/itsnpworkshop",
    "Github": "https://github.com/itsnporg",
    "Live": "https://tiny.cc/itsnplive",
    "Feedback": "https://tiny.cc/itsnpfeedback",
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
        (
            "Server Creation",
            f"<t:{guild.created_at.timestamp():.0f}:F> • <t:{guild.created_at.timestamp():.0f}:R>",
            True,
        ),
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

    embed = Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
    )
    fields = [
        ("ID", member.id, True),
        ("Joined on", f"<t:{joined_at}:F> • <t:{joined_at}:R>", True),
        ("Created on", f"<t:{created_at}:F> • <t:{created_at}:R>", True),
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
        title=f"{await ctx.rest.fetch_my_user()}'s Information",
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
        description=f"```Language : Python\nPython Version : {python_version()}\nBot Version : {bot_version}\nLibrary : hikari.py\nCommand Handler :\nhikari-tanjun(Slash Commands)\nhikari-lightbulb(Message Commands)\nHikari Version : {hikari_version}\nTanjun Version : {tanjun_version}\nLightbulb Version : {lighbulb_version}\nUptime : {pretty_uptime}\nCPU Time : {pretty_cpu_time}\nMemory Usage : {mem_usage:,.3f} MiB /{mem_total:,.0f} MiB\nPrefix : /\nClient ID : {bot.id}```",
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

    await ctx.respond(embed=embed, component=button)


@component.with_slash_command
@tanjun.with_str_slash_option("country", "A country's name")
@tanjun.as_slash_command("countryinfo", "Get info about a country")
async def countryinfo_command(ctx: tanjun.abc.Context, *, country: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://restcountries.eu/rest/v2/name/{country}"
        ) as resp:
            info = await resp.json()
            try:
                country_name = info[0]["name"]
                top_level_domainn = info[0]["topLevelDomain"]
                top_level_domain = ",".join(top_level_domainn)
                alpha_2_code = info[0]["alpha2Code"]
                calling_codes_list = info[0]["callingCodes"]
                calling_codes = ",".join(calling_codes_list)
                capital = info[0]["capital"]
                region = info[0]["region"]
                population = info[0]["population"]
                native_name = info[0]["nativeName"]
                time_zones_list = info[0]["timezones"]
                time_zones = ",".join(time_zones_list)
                currencies = info[0]["currencies"]
                currency_code = currencies[0]["code"]
                currency_symbol = currencies[0]["symbol"]
                alternative_spellings_list = info[0]["altSpellings"]
                alternative_spellings = ",".join(alternative_spellings_list)
            except KeyError:
                return await ctx.respond("No Country found :(")
    embed = Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
        title=f"Info of {country_name}",
    )
    fields = [
        ("Name", country_name, True),
        ("Capital", capital, True),
        ("Top Level Domain", top_level_domain, True),
        ("Alpha2 Code", alpha_2_code, True),
        ("Calling Codes", calling_codes, True),
        ("Region", region, True),
        ("Population", population, True),
        ("Native Name", native_name, True),
        ("Time Zones", time_zones, True),
        ("Currency Code", currency_code, True),
        ("Currency Symbol", currency_symbol, True),
        ("Alternative Spellings", alternative_spellings, True),
    ]

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    embed.set_thumbnail(f"https://flagcdn.com/w80/{str(alpha_2_code).lower()}.png")
    embed.set_footer(text=f"Requested by {ctx.author}")
    button = create_source_button(ctx, "https://restcountries.eu")
    await ctx.respond(embed=embed, component=button)


@component.with_slash_command
@tanjun.with_str_slash_option("city", "A city's name")
@tanjun.as_slash_command("weather", "Get a place's weather.")
async def weather_command(ctx: tanjun.abc.Context, *, city: str) -> None:
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = (
        base_url + "appid=" + (os.environ.get("WEATHER_TOKEN")) + "&q=" + city
    )
    image = "https://icons-for-free.com/iconfiles/png/512/fog+foggy+weather+icon-1320196634851598977.png"
    async with aiohttp.ClientSession() as session:
        async with session.get(complete_url) as resp:
            data = await resp.json()
            try:
                main = data["main"]
                wind = data["wind"]
                weather = data["weather"]
                city = data["name"]
                temperature_in_celcius = int(main["temp"] - 273)
                feelslike_in_celcius = int(main["feels_like"] - 273)
                max_tempr = int(main["temp_max"] - 273)
                min_tempr = int(main["temp_min"] - 273)
                wind = data["wind"]
                speed_wind = wind["speed"]
                weather_description = str(weather[0]["description"]).title()
            except KeyError:
                return await ctx.respond("No City was found :(")
        embed = Embed(
            color=0xF1C40F,
            timestamp=datetime.now().astimezone(),
            title=f"Weather of {city.title()}",
        )

    fields = [
        ("Temperature", f"{temperature_in_celcius} °C", True),
        ("Feels Like", f"{feelslike_in_celcius} °C", True),
        ("Maximum Temperature", f"{max_tempr} °C", True),
        ("Minimum Temperature", f"{min_tempr} °C", True),
        ("Description", weather_description, True),
        ("Wind Velocity", f"{speed_wind} km/h", True),
    ]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_thumbnail(image)

    button = create_source_button(ctx, "https://openweathermap.org/api")
    await ctx.respond(embed=embed, component=button)


@component.with_slash_command
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

    embed = Embed(
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


@component.with_slash_command
@tanjun.as_slash_command("botinvite", "Invite Link for the bot")
async def botinvite_command(ctx: tanjun.abc.Context) -> None:
    """Sends a invite link for the bot"""
    bot_user = await ctx.rest.fetch_my_user()
    await ctx.respond(
        f"https://discord.com/api/oauth2/authorize?client_id={bot_user.id}&permissions=8&scope=bot%20applications.commands"
    )


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
