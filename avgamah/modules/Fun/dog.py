from datetime import datetime

import aiohttp
import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import create_source_button

dog_component = tanjun.Component()


@dog_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_cooldown("Fun")
@tanjun.as_slash_command("dog", "Return a dog gif.", default_to_ephemeral=True)
async def dog_command(ctx: tanjun.abc.Context) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://some-random-api.ml/animal/dog") as resp:
            dog_json = await resp.json()

    embed = hikari.Embed(
        color=0xF1C40F,
        timestamp=datetime.now().astimezone(),
        description=f"```{dog_json['fact']}```",
    )
    embed.set_author(name="Here's a dog for you!")
    embed.set_image(dog_json["image"])
    embed.set_footer(text=f"Requested by {ctx.author}")
    button = create_source_button(ctx, "https://some-random-api.ml/")

    await ctx.respond(embed=embed, component=button)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(dog_component.copy())
