import asyncio
import hikari
from hikari import Embed
import aiohttp
from datetime import datetime
import tanjun
from hikari.interactions.base_interactions import ResponseType

from itsnp.core.client import Client

component = tanjun.Component()


@component.with_slash_command
@tanjun.as_slash_command("cat", "Return a cat gif.", default_to_ephemeral=True)
async def cat_command(ctx: tanjun.abc.Context) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://some-random-api.ml/animal/cat") as resp:
            cat_json = await resp.json()

    embed = Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
        description=f"```{cat_json['fact']}```",
    )
    embed.set_author(name=f"Here's a cat for you!")
    embed.set_image(cat_json["image"])
    embed.set_footer(text=f"Requested by {ctx.author}")

    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_component(client: Client) -> None:
    client.add_component(component.copy())
