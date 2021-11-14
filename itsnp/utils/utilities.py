from __future__ import annotations

import asyncio
import re
import typing as t
from operator import attrgetter

import hikari
import tanjun

_ValueT = t.TypeVar("_ValueT")
T = t.TypeVar("T")

TRUE_RESP = ["yes", "y", "ye", "t", "true"]
FALSE_RESP = ["no", "n", "false", "fa", "fal"]


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


async def collect_response(  # pylint: disable=too-many-branches
    ctx: tanjun.SlashContext,
    validator: list[str] | t.Callable | None = None,
    timeout: int = 60,
    timeout_msg: str = "Waited for 60 seconds... Timeout.",
) -> hikari.GuildMessageCreateEvent | None:
    """
    Helper function to collect a user response.

    Parameters
    ==========
    ctx: SlashContext
        The context to use.
    validator: list[str] | Callable | None = None
        A validator to check against. Validators can be:
            - list - A list of strings to match against.
            - Callable/Function - A function accepting (ctx, event) and returning bool.
            - None - Skips validation and returns True always.
    timeout int = 60
        The default wait_for timeout to use.
    timeout_msg: str = Waited for 60 seconds ... Timeout.
        The message to display if a timeout occurs
    """

    def is_author(event: hikari.GuildMessageCreateEvent):
        if ctx.author == event.message.author:
            return True
        return False

    while True:
        try:
            event = await ctx.client.events.wait_for(
                hikari.GuildMessageCreateEvent, predicate=is_author, timeout=timeout
            )
        except asyncio.TimeoutError:
            await ctx.edit_initial_response(timeout_msg)
            return None

        if event.content == "❌":
            return None

        if not validator:
            return event

        if isinstance(validator, list):
            if any(
                valid_resp.lower() == event.content.lower() for valid_resp in validator
            ):
                return event
            validation_message = await ctx.respond(
                f"That wasn't a valid response... Expected one these: {' - '.join(validator)}"
            )
            await asyncio.sleep(3)
            await validation_message.delete()

        elif asyncio.iscoroutinefunction(validator):
            valid = await validator(ctx, event)
            if valid:
                return event
            validation_message = await ctx.respond(
                "That doesn't look like a valid response... Try again?"
            )
            await asyncio.sleep(3)
            await validation_message.delete()

        elif callable(validator):
            if validator(ctx, event):
                return event
            validation_message = await ctx.respond(
                "Something about that doesn't look right... Try again?"
            )
            await asyncio.sleep(3)
            await validation_message.delete()


def is_int_validator(_, event: hikari.GuildMessageCreateEvent) -> bool:
    """
    Used as a validator for `collect_response` to ensure the message content is an integer.
    """
    try:
        if event.content:
            int(event.content)
            return True
    except ValueError:
        pass
    return False


async def ensure_guild_channel_validator(ctx: tanjun.abc.Context, event) -> bool:
    """
    Used as a validator for `collect_response` to ensure a text channel in a guild exists.
    """
    guild = ctx.get_guild()
    if not guild:
        return False
    channels = guild.get_channels() if guild else []
    found_channel = None

    for channel_id in channels:
        channel = guild.get_channel(channel_id)
        if str(channel.id) in event.content or channel.name == event.content:
            found_channel = channel
            break

    if found_channel:
        return True

    await ctx.edit_initial_response(
        content=f"Channel `{event.content}` not found! Try again?"
    )
    await event.message.delete()
    await asyncio.sleep(5)
    return False


def yes_no_answer_validator(
    _: tanjun.abc.SlashContext, event: hikari.GuildMessageCreateEvent
):
    """Validator for collect_response that checks for yes/no answers."""
    if event.content.lower() in TRUE_RESP:
        return True
    if event.content.lower() in FALSE_RESP:
        return True
    return False
