import tanjun
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
