import aiohttp
import hikari
import tanjun

from avgamah.core import Client

from . import zodiac_signs

rashifal_component = tanjun.Component()


@rashifal_component.with_slash_command
@tanjun.with_str_slash_option(
    "zodiac", "Your zodiac Sign", choices=[sign for sign in zodiac_signs], default=None
)
@tanjun.as_slash_command("rashifal", "View your today's rashifal.")
async def rashifal(ctx: tanjun.abc.Context, zodiac: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://rashifal-api.herokuapp.com/api/{zodiac}") as r:
            response = await r.json()

        if r.status != 200:
            raise tanjun.CommandError(
                f"Got an error while sending the request.\nError```py\n{r.status}\n{r.reason}"
            )
    await ctx.respond(
        embed=hikari.Embed(
            title=f"{response['sun_sign']} राशिको राशिफल।",
            description=response["prediction"],
            color=0x00FF00,
        ).set_footer(text=response["date"])
    )


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(rashifal_component.copy())
