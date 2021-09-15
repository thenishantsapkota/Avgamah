import typing as t

import hikari
import tanjun
from hikari import Embed


class Errors:
    def embed(self, ctx: tanjun.abc.Context, message: str) -> Embed:
        desc: str
        desc = f"Uh Oh! {message}"
        embed = Embed(
            description=desc,
            color=hikari.Color(0xFF0000),
        )
        embed.set_footer("An error has occurred!")

        return embed

    @staticmethod
    async def parse(exc: Exception) -> None:
        print(exc)
        raise exc

    async def parse_tanjun(
        self, ctx: tanjun.abc.Context, exc: t.Union[tanjun.CommandError, Exception]
    ) -> None:
        if isinstance(
            exc, (tanjun.NotEnoughArgumentsError, tanjun.TooManyArgumentsError)
        ):
            await ctx.respond(self.embed(ctx, f"**Error**```{exc.message}```"))
            raise exc

        elif isinstance(exc, tanjun.MissingDependencyError):
            await ctx.respond(self.embed(ctx, f"**Error**```{exc.message}```"))
            raise exc

        else:
            print(exc)
            raise exc
