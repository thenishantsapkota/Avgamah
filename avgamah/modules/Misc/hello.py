import random

import hikari
import tanjun

from avgamah.core.client import Client
from avgamah.utils.buttons import DELETE_ROW

hello_component = tanjun.Component()


@hello_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.as_slash_command("hello", "Greet the user with hello.")
async def hello_command(ctx: tanjun.abc.Context) -> None:
    greeting = random.choice(("Hello", "Hi", "Hey"))
    await ctx.respond(
        f"{greeting} {ctx.member.mention}!", user_mentions=True, component=DELETE_ROW
    )


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(hello_component.copy())
