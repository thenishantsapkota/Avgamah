import hikari
import tanjun

from avgamah.core.client import Client

pussy_component = tanjun.Component()


@pussy_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_nsfw_check
@tanjun.as_slash_command("pussy", "Cute pussy cats.")
async def pussy(ctx: tanjun.abc.Context):
    await ctx.shards.reddit_cache.reddit_sender(ctx, "pussy")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(pussy_component.copy())
