import tanjun

from itsnp.core.client import Client

ass_component = tanjun.Component()


@ass_component.with_slash_command
@tanjun.with_nsfw_check
@tanjun.as_slash_command("ass", "Juicy Asses mmm...")
async def ass(ctx: tanjun.abc.Context):
    await ctx.shards.reddit_cache.reddit_sender(ctx, "ass")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(ass_component.copy())
