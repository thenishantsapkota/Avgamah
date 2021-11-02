import tanjun

from itsnp.core.client import Client

cursedcomments_component = tanjun.Component()


@cursedcomments_component.with_slash_command
@tanjun.as_slash_command("cursedcomments", "Get a random post from r/cursedcomments")
async def cursedcomments(ctx: tanjun.abc.Context):
    await ctx.shards.reddit_cache.reddit_sender(ctx, "cursedcomments")


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(cursedcomments_component.copy())
