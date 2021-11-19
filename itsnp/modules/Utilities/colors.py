import logging

import hikari
import tanjun

from itsnp.core import Client
from itsnp.modules.Utilities.embeds import EMBED_MENU
from itsnp.utils.utilities import get
from models import ColorModel

from . import color_dict, permissions

color_component = tanjun.Component()

COLOR_MENU = {
    "Crimson": {"title": "Crimson", "style": hikari.ButtonStyle.PRIMARY},
    "Green": {"title": "Green", "style": hikari.ButtonStyle.PRIMARY},
    "Yellow": {"title": "Yellow", "style": hikari.ButtonStyle.PRIMARY},
    "Cyan": {"title": "Cyan", "style": hikari.ButtonStyle.PRIMARY},
    "Magenta": {"title": "Magenta", "style": hikari.ButtonStyle.PRIMARY},
    "Red": {"title": "Red", "style": hikari.ButtonStyle.PRIMARY},
    "Orange": {"title": "Orange", "style": hikari.ButtonStyle.PRIMARY},
    "Blurple": {"title": "Blurple", "style": hikari.ButtonStyle.PRIMARY},
    "Silver": {"title": "Silver", "style": hikari.ButtonStyle.PRIMARY},
    "Pink": {"title": "Pink", "style": hikari.ButtonStyle.PRIMARY},
}


def build_menu(ctx: tanjun.abc.Context):
    menu = []
    menu_count = 0
    last_menu_item = list(EMBED_MENU)[-1]
    row = ctx.rest.build_action_row()

    for emote, options in COLOR_MENU.items():
        (
            row.add_button(options["style"], emote)
            .set_label(options["title"])
            .add_to_container()
        )
        menu_count += 1
        if menu_count == 5 or last_menu_item == emote:
            menu.append(row)
            row = ctx.rest.build_action_row()
            menu_count = 0

    return menu


@color_component.with_slash_command
@tanjun.as_slash_command("color", "Setup color roles for the server.")
async def colors(ctx: tanjun.abc.Context) -> None:
    menu = build_menu(ctx)
    guild = ctx.get_guild()
    await permissions.admin_role_check(ctx, guild)
    for name, color in color_dict.items():
        role = get(await ctx.rest.fetch_roles(guild), name=name)
        if role is None:
            color_role = await ctx.rest.create_role(guild=guild, name=name, color=color)
            await ColorModel.get_or_create(
                guild_id=ctx.guild_id, role_id=color_role.id, role_name=color_role.name
            )
    embed = hikari.Embed(
        title="Colors",
        color=0x00FF00,
    )
    embed.set_image(
        "https://cdn.discordapp.com/attachments/853175466751295499/910075028803055626/unknown.png"
    )

    await ctx.get_channel().send(embed=embed, components=[*menu])
    await ctx.respond("Done, You can now delete this message.")


@color_component.with_listener(hikari.InteractionCreateEvent)
async def listen_for_color_buttons(
    event: hikari.InteractionCreateEvent,
) -> None:
    if (
        not isinstance(event.interaction, hikari.ComponentInteraction)
        or event.interaction.custom_id not in COLOR_MENU.keys()
    ):
        return

    try:
        color_model = await ColorModel.filter(guild_id=event.interaction.guild_id)

    except Exception as e:
        logging.warn(f"Exception {e} occured in {event.interaction.guild_id}")
        return

    role_ids = [model.role_id for model in color_model]
    role_names = [model.role_name for model in color_model]

    roles = {name: id for id, name in zip(role_ids, role_names)}

    for id in event.interaction.member.role_ids:
        if id in role_ids:
            await event.interaction.member.remove_role(id)

    await event.interaction.member.add_role(roles[event.interaction.custom_id])
    await event.interaction.edit_initial_response("Done!")


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(color_component.copy())
