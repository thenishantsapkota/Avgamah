from datetime import datetime
import random
import asyncio

import hikari
from hikari.interactions.base_interactions import ResponseType
import tanjun
from hikari import Embed

from itsnp.core.client import Client

component = tanjun.Component()

LINKS_DICT = {
    "Facebook": "https://tiny.cc/itsnpfb",
    "Facebook Group": "https://www.facebook.com/groups/techforimpact",
    "Instagram": "https://tiny.cc/itsnpig",
    "Discord": "https://tiny.cc/itsnpdiscord",
    "Twitter": "https://tiny.cc/itsnptwitter",
    "Youtube": "https://tiny.cc/itsnpyt",
    "Donate Us": "https://tiny.cc/itsnpdonate",
    "Workshop": "https://tiny.cc/workshop",
    "Github": "https://github.com/itsnporg",
    "Live": "https://tiny.cc/itsnplive",
}

PLATFORM = LINKS_DICT.keys()


@component.with_slash_command
@tanjun.as_slash_command("hello", "Greet the user with hello.")
async def hello_command(ctx: tanjun.abc.Context) -> None:
    greeting = random.choice(("Hello", "Hi", "Hey"))
    await ctx.respond(f"{greeting} {ctx.member.mention}!", user_mentions=True)


@component.with_slash_command
@tanjun.as_slash_command("ping", "Return bot ping.", default_to_ephemeral=True)
async def ping_command(ctx: tanjun.abc.Context) -> None:
    heartbeat_latency = (
        ctx.shards.heartbeat_latency * 1_000 if ctx.shards else float("NAN")
    )
    embed = Embed(
        description=f"I pinged the API and got these results.\n**Gateway:** {heartbeat_latency:.0f}ms",
        color=0xF1C40F,
    )
    embed.set_author(name="Ping")
    await ctx.respond(embed)


@component.with_slash_command
@tanjun.with_str_slash_option(
    "platform", "The link to show", choices=(l.lower() for l in PLATFORM)
)
@tanjun.as_slash_command("link", "Show different ITSNP link.")
async def link_command(ctx: tanjun.abc.Context, name: str) -> None:
    await ctx.respond(LINKS_DICT[name.title()])


@component.with_slash_command
@tanjun.as_slash_command("links", "Show all ITSNP Links.")
async def links_command(ctx: tanjun.abc.Context) -> None:
    select_menu = (
        ctx.rest.build_action_row()
        .add_select_menu("link_select")
        .set_placeholder("Choose a link")
    )

    for option in PLATFORM:
        select_menu.add_option(option, option.lower()).add_to_menu()
    await ctx.respond(
        "Select a link from dropdown.", component=select_menu.add_to_container()
    )

    try:
        event = await ctx.client.events.wait_for(
            hikari.InteractionCreateEvent, timeout=60
        )
    except asyncio.TimeoutError:
        await ctx.edit_initial_response("Timed out!", components=[])

    else:
        await ctx.edit_initial_response(
            LINKS_DICT[f"{event.interaction.values[0].title()}"], components=[]
        )


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


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
