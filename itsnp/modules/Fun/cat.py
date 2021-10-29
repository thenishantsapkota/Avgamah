from datetime import datetime

import aiohttp
import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import create_source_button

cat_component = tanjun.Component()


@cat_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command("cat", "Return a cat gif.", default_to_ephemeral=True)
async def cat_command(ctx: tanjun.abc.Context) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://some-random-api.ml/animal/cat") as resp:
            cat_json = await resp.json()

    embed = hikari.Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
        description=f"```{cat_json['fact']}```",
    )
    embed.set_author(name="Here's a cat for you!")
    embed.set_image(cat_json["image"])
    embed.set_footer(text=f"Requested by {ctx.author}")
    button = create_source_button(ctx, "https://some-random-api.ml/")

    await ctx.respond(embed=embed, component=button)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(cat_component.copy())
