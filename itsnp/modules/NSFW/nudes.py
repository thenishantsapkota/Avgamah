import tanjun

from itsnp.core.client import Client

nudes_component = tanjun.Component()


@nudes_component.with_slash_command
@tanjun.with_nsfw_check
@tanjun.as_slash_command("nudes", "I like Noodles")
async def nudes(ctx: tanjun.abc.Context):
    await ctx.shards.reddit_cache.reddit_sender(ctx, "Nudes")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(nudes_component.copy())
