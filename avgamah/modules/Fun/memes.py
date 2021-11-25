import hikari
import tanjun

from avgamah.core.client import Client

memes_component = tanjun.Component()


@memes_component.with_slash_command
@tanjun.with_cooldown("Fun")
@tanjun.as_slash_command("memes", "Get a random meme")
async def meme(ctx: tanjun.abc.Context):
    await ctx.shards.reddit_cache.reddit_sender(ctx, "memes")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(memes_component.copy())
