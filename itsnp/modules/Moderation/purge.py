from __future__ import annotations

import asyncio
import re
from datetime import datetime, timedelta, timezone

import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.utilities import iter_messages

from . import permissions

purge_component = tanjun.Component()

MAX_MESSAGE_BULK_DELETE = timedelta(weeks=2)


@purge_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.MANAGE_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.READ_MESSAGE_HISTORY
)
@tanjun.with_str_slash_option(
    "after",
    "ID of a message to delete messages which were sent after.",
    converters=tanjun.to_snowflake,
    default=None,
)
@tanjun.with_str_slash_option(
    "before",
    "ID of a message to delete messages which were sent before.",
    converters=tanjun.to_snowflake,
    default=None,
)
@tanjun.with_bool_slash_option(
    "bot_only",
    "Whether this should only delete messages sent by bots and webhooks.",
    default=False,
)
@tanjun.with_bool_slash_option(
    "human_only",
    "Whether this should only delete messages sent by actual users.",
    default=False,
)
@tanjun.with_bool_slash_option(
    "has_attachments",
    "Whether this should only delete messages which have attachments.",
    default=False,
)
@tanjun.with_bool_slash_option(
    "has_embeds",
    "Whether this should only delete messages which have embeds.",
    default=False,
)
@tanjun.with_str_slash_option(
    "regex",
    "A regular expression to match against the message content.",
    converters=re.compile,
    default=None,
)
@tanjun.with_member_slash_option(
    "user",
    "User to delete messages for",
    default=None,
)
@tanjun.with_int_slash_option(
    "count", "The amount of messages to delete.", default=None
)
@tanjun.as_slash_command("purge", "purge new messages from chat as a moderator.")
async def purge_command(
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
) -> None:
    """Clear new messages from chat.
    !!! NOTE
        This can only be used on messages under 14 days old.
    Arguments:
        * count: The amount of messages to delete.
    Options:
        * users (user): Mentions and/or IDs of the users to delete messages from.
        * human only (human): Whether this should only delete messages sent by actual users.
            This defaults to false and will be set to true if provided without a value.
        * bot only (bot): Whether this should only delete messages sent by bots and webhooks.
        * before  (before): ID of a message to delete messages which were sent before.
        * after (after): ID of a message to delete messages which were sent after.
        * suppress (-s, --suppress): Provided without a value to stop the bot from sending a message once the
            command's finished.
    """
    await permissions.mod_role_check(ctx, ctx.get_guild())
    if human_only and bot_only:
        raise tanjun.CommandError("Can only specify one of `human` or `bot`")

    now = datetime.now(tz=timezone.utc)
    after_too_old = after and now - after.created_at >= MAX_MESSAGE_BULK_DELETE
    before_too_old = before and now - before.created_at >= MAX_MESSAGE_BULK_DELETE

    if after_too_old or before_too_old:
        raise tanjun.CommandError("Cannot delete messages that are over 14 days old")

    iterator = (
        iter_messages(
            ctx,
            count,
            after,
            before,
            bot_only,
            human_only,
            has_attachments,
            has_embeds,
            regex,
            user,
        )
        .filter(lambda message: now - message.created_at < MAX_MESSAGE_BULK_DELETE)
        .map(lambda x: x.id)
        .chunk(100)
    )

    async for messages in iterator:
        await ctx.rest.delete_messages(ctx.channel_id, *messages)
        break

    await ctx.respond(content="Purged messages.")
    await asyncio.sleep(5)
    try:
        await ctx.delete_last_response()
    except hikari.NotFoundError:
        pass


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(purge_component.copy())
