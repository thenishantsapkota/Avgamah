import hikari
import tanjun
import yuyo
from hikari.api.special_endpoints import ActionRowBuilder
from hikari.messages import ButtonStyle


def create_source_button(ctx: tanjun.abc.Context, source: str) -> ActionRowBuilder:
    button = (
        ctx.rest.build_action_row()
        .add_button(ButtonStyle.LINK, source)
        .set_label("Source")
        .add_to_container()
    )

    return button


async def delete_message_button(ctx: yuyo.ComponentContext) -> None:
    if (
        ctx.interaction.message
        and ctx.interaction.message.interaction.user.id == ctx.interaction.user.id
    ):
        await ctx.defer(hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)
        await ctx.delete_initial_response()

    else:
        await ctx.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            f"This button belongs to someone else.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


DELETE_CUSTOM_ID = "AUTHOR_DELETE_BUTTON"
DELETE_ROW = (
    hikari.impl.ActionRowBuilder()
    .add_button(hikari.ButtonStyle.SECONDARY, DELETE_CUSTOM_ID)
    .set_emoji(915250243929509918)
    .add_to_container()
)
