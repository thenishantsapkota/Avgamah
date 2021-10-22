from datetime import datetime

import aiohttp
import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.pagination import paginate
from itsnp.utils.utilities import _chunk

urban_component = tanjun.Component()


@urban_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("term", "Term to Search for")
@tanjun.as_slash_command("urban", "Search a term on urban dictionary")
async def urban_command(ctx: tanjun.abc.Context, term: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.urbandictionary.com/v0/define?term={term}"
        ) as resp:
            raw = await resp.json()

    urban_data = raw["list"]
    if not urban_data:
        return await ctx.respond("No Results :(")

    fields = (
        (
            hikari.UNDEFINED,
            hikari.Embed(
                title=f"Definition for {term}",
                color=0x00FF00,
                timestamp=datetime.now().astimezone(),
            )
            .add_field(name="Definition", value=data[0]["definition"])
            .add_field(name="Example", value=data[0]["example"])
            .add_field(name="Link", value=data[0]["permalink"])
            .set_footer(f"Page {index+1}/{len(urban_data)}")
            .set_thumbnail(
                "https://images.squarespace-cdn.com/content/v1/586bd48d03596e5605450cee/1484851165621-U1SMXTW7C9X3BB3IEQ2U/image-asset.jpeg?format=1000w"
            ),
        )
        for index, data in enumerate(_chunk(urban_data, 1))
    )
    await paginate(ctx, fields, 180)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(urban_component.copy())
