from datetime import datetime

import hikari
import tanjun

from avgamah.core.client import Client

hentai_component = tanjun.Component()


@hentai_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_nsfw_check
@tanjun.as_slash_command("hentai", "Get some juicy hentai...Yum!!")
async def hentai(ctx: tanjun.abc.Context):
    await ctx.shards.reddit_cache.reddit_sender(ctx, "hentai")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(hentai_component.copy())
