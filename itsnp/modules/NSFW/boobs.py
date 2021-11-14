import tanjun

from itsnp.core.client import Client

boobs_component = tanjun.Component()


@boobs_component.with_slash_command
@tanjun.with_nsfw_check
@tanjun.as_slash_command("boobs", "Boobies")
async def boobs(ctx: tanjun.abc.Context):
    await ctx.shards.reddit_cache.reddit_sender(ctx, "boobs")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(boobs_component.copy())
