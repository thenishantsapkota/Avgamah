from __future__ import annotations

import typing as t
from datetime import timedelta

import tanjun
import yuyo


async def paginate(
    ctx: tanjun.abc.Context,
    fields: t.Generator[tuple | list],
    timeout: float | str,
):
    """
    A helper function that assists in generating embed paginations by passing in a generator and timeout value.

    Parameters
    ----------
    ctx : tanjun.abc.Context
        Context of the command invokation
    fields : t.Generator[tuple | list]
        Generator object containing the embeds to be generated.
    timeout : float
        Timeout of the pagination(in seconds)
    """
    paginator = yuyo.ComponentPaginator(
        fields,
        authors=(ctx.author.id,),
        timeout=timedelta(seconds=timeout),
        triggers=(
            yuyo.pagination.LEFT_DOUBLE_TRIANGLE,
            yuyo.pagination.LEFT_TRIANGLE,
            yuyo.pagination.STOP_SQUARE,
            yuyo.pagination.RIGHT_TRIANGLE,
            yuyo.pagination.RIGHT_DOUBLE_TRIANGLE,
        ),
    )

    if first_response := await paginator.get_next_entry():
        content, embed = first_response
        message = await ctx.respond(
            content=content,
            component=paginator,
            embed=embed,
            ensure_result=True,
        )
        ctx.shards.component_client.set_executor(message, paginator)
        return
