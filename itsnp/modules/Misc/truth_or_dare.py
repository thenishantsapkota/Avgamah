import aiohttp
import hikari
import tanjun

from itsnp.core.client import Client

truth_or_dare_component = tanjun.Component()


@truth_or_dare_component.with_slash_command
@tanjun.with_str_slash_option(
    "category",
    "Type of Truth or Dare",
    choices=(
        "friendly",
        "dirty",
    ),
)
@tanjun.with_str_slash_option(
    "type",
    "Truth or Dare?",
    choices=(
        "truth",
        "dare",
    ),
)
@tanjun.as_slash_command("truth_or_dare", "Send a random question of Truth or Dare.")
async def truth_or_dare(ctx: tanjun.abc.Context, type: str, category: str) -> None:
    data = {"category": category, "type": type}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://randommer.io/truth-dare-generator", data=data
        ) as resp:
            response = await resp.json()

    embed = hikari.Embed(
        title=f"{type.title()} Question",
        description=response["text"],
        color=0x00FF00 if category == "friendly" else 0xFF0000,
    ).set_footer(f"Invoked by {ctx.author}")

    await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(truth_or_dare_component.copy())
