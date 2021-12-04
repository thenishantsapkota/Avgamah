import tanjun

from avgamah.core import Client

from . import times, zodiac_signs

rashifal_component = tanjun.Component()


@rashifal_component.with_slash_command
@tanjun.with_str_slash_option(
    "duration",
    "Duration of the rashifal you wanna see",
    choices=[time for time in times.values()],
)
@tanjun.with_str_slash_option(
    "zodiac", "Your zodiac Sign", choices=[sign for sign in zodiac_signs.keys()]
)
@tanjun.as_slash_command("rashifal", "View your today's rashifal.")
async def rashifal(ctx: tanjun.abc.Context, zodiac: str, duration: str) -> None:
    await ctx.shards.rashifal_cache.rashifal_sender(ctx, zodiac, duration)


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(rashifal_component.copy())
