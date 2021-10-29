import hikari
import tanjun
from hikari.messages import ButtonStyle

from itsnp.core.client import Client

links_component = tanjun.Component()

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


@links_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option(
    "platform",
    "The link to show",
    choices=(choice.lower() for choice in PLATFORM),
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


@links_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
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


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(links_component.copy())
