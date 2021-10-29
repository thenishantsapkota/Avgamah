from __future__ import annotations

import re
import typing as t
from operator import attrgetter

import hikari
import tanjun

_ValueT = t.TypeVar("_ValueT")
T = t.TypeVar("T")


def _chunk(iterator: t.Iterator[_ValueT], max: int) -> t.Iterator[list[_ValueT]]:
    chunk: list[_ValueT] = []
    for entry in iterator:
        chunk.append(entry)
        if len(chunk) == max:
            yield chunk
            chunk = []

    if chunk:
        yield chunk


def get(iterable: t.Iterable[T], **attrs: t.Any) -> t.Optional[T]:
    """A helper that returns the first element in the iterable that meets
    all the traits passed in ``attrs``.
    Args:
        iterable (Iterable): An iterable to search through.
        **attrs (Any): Keyword arguments that denote attributes to search with.
    """
    attrget = attrgetter

    # Special case the single element call
    if len(attrs) == 1:
        k, v = attrs.popitem()
        pred = attrget(k.replace("__", "."))
        for elem in iterable:
            if pred(elem) == v:
                return elem
        return None

    converted = [
        (attrget(attr.replace("__", ".")), value) for attr, value in attrs.items()
    ]

    for elem in iterable:
        if all(pred(elem) == value for pred, value in converted):
            return elem
    return None


def iter_messages(
    ctx: tanjun.abc.Context,
    count: int | None,
    after: hikari.Snowflake | None,
    before: hikari.Snowflake | None,
    bot_only: bool,
    human_only: bool,
    has_attachments: bool,
    has_embeds: bool,
    regex: re.Pattern[str] | None,
    user: hikari.User,
) -> hikari.LazyIterator[hikari.Message]:
    if count is None and after is not None:
        raise tanjun.CommandError("Must specify `count` when `after` is not specified")

    elif count is not None and count <= 0:
        raise tanjun.CommandError("Count must be greater than 0.")

    if before is None and after is None:
        before = hikari.Snowflake.from_datetime(ctx.created_at)

    iterator = ctx.rest.fetch_messages(
        ctx.channel_id,
        before=hikari.UNDEFINED if before is None else before,
        after=(hikari.UNDEFINED if after is None else after)
        if before is None
        else hikari.UNDEFINED,
    )

    if before and after:
        iterator = iterator.filter(lambda message: message.id > after)

    if human_only:
        iterator = iterator.filter(lambda message: not message.author.is_bot)

    elif bot_only:
        iterator = iterator.filter(lambda message: message.author.is_bot)

    if has_attachments:
        iterator = iterator.filter(lambda message: bool(message.attachments))

    if has_embeds:
        iterator = iterator.filter(lambda message: bool(message.embeds))

    if regex:
        iterator = iterator.filter(
            lambda message: bool(message.content and regex.match(message.content))
        )

    if user is not None:
        iterator = iterator.filter(lambda message: message.author.id)
    if count:
        iterator = iterator.limit(count + 1)

    return iterator
