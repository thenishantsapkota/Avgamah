import aiohttp
import hikari
import tanjun

from avgamah.core.client import Client

joke_component = tanjun.Component()


@joke_component.with_slash_command
@tanjun.with_str_slash_option(
    "type",
    "Type of joke",
    choices=(
        "single",
        "twopart",
    ),
)
@tanjun.with_str_slash_option(
    "category",
    "Category of joke you want",
    choices=(
        "programming",
        "miscellaneous",
        "dark",
        "pun",
        "spooky",
        "any",
    ),
)
@tanjun.as_slash_command("joke", "Get a joke.", default_to_ephemeral=True)
async def joke_programming(ctx: tanjun.abc.Context, category: str, type: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://v2.jokeapi.dev/joke/{category}?type={type}"
        ) as resp:
            response = await resp.json()

    if type == "single":
        await ctx.respond(
            embed=hikari.Embed(description=response["joke"], color=0x00FF00)
        )

    if type == "twopart":
        await ctx.respond(
            embed=hikari.Embed(
                description=f"{response['setup']}\n\n||{response['delivery']}||",
                color=0x00FF00,
            )
        )


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(joke_component.copy())
