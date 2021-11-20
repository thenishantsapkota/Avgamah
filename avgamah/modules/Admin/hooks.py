import json

import hikari
import tanjun

from avgamah.core import Client

hooks = tanjun.AnyHooks()
component = tanjun.Component()


@hooks.with_on_error
async def on_error(ctx: tanjun.abc.Context, error: Exception) -> None:
    if isinstance(error, hikari.ForbiddenError):
        embed = hikari.Embed(
            title=error.message,
            description=f"I cannot run this command because I am missing permissions.\nCheck my permissions.\n\nError: ```{error}```",
            color=0xFF0000,
        )
        await ctx.respond(embed=embed)


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(component.copy())
    client.set_hooks(hooks)
