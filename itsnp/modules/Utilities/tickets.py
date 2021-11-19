from __future__ import annotations

from datetime import datetime

import hikari
import tanjun
from hikari.internal.cache import CacheMappingView
from hikari.messages import ButtonStyle

from itsnp.core.client import Client
from itsnp.utils.utilities import FALSE_RESP, collect_response, yes_no_answer_validator

DEFAULT_TIMEOUT = 60

ticket_component = tanjun.Component()


@ticket_component.with_listener(hikari.InteractionCreateEvent)
async def listen_for_ticket(
    event: hikari.InteractionCreateEvent,
    bot: hikari.GatewayBot = tanjun.injected(type=hikari.GatewayBotAware),
) -> None:
    if not isinstance(
        event.interaction, hikari.ComponentInteraction
    ) or event.interaction.custom_id not in ["new_ticket", "close_ticket"]:
        return

    if event.interaction.custom_id == "close_ticket":
        await event.app.rest.edit_channel(
            event.interaction.channel_id,
            permission_overwrites=[
                hikari.PermissionOverwrite(
                    id=event.interaction.member,
                    type=1,
                    deny=hikari.Permissions.VIEW_CHANNEL,
                ),
                hikari.PermissionOverwrite(
                    id=event.interaction.guild_id,
                    type=0,
                    deny=hikari.Permissions.VIEW_CHANNEL,
                ),
            ],
        )
        await event.interaction.get_channel().send(
            "Closed the Ticket, You can store it or delete it."
        )
        return

    ticket_channel = None
    tickets_category = None
    guild: hikari.GatewayGuild = event.interaction.get_guild()
    roles: CacheMappingView = guild.get_roles()
    default_role: hikari.Role = guild.get_role(roles.get_item_at(0))
    await event.interaction.edit_initial_response("Let's get this started!")
    for channel_id in guild.get_channels():
        channel: hikari.GuildTextChannel | hikari.GuildCategory = guild.get_channel(
            channel_id
        )
        if (
            channel.name.lower() == "tickets"
            and channel.type == hikari.ChannelType.GUILD_CATEGORY
        ):
            tickets_category = channel
        elif (
            str(event.interaction.member.id) in channel.name
            and channel.name.endswith("-ticket")
            and channel.type == hikari.ChannelType.GUILD_TEXT
        ):
            ticket_channel = channel

    if not ticket_channel:
        ticket_channel = await guild.create_text_channel(
            name=f"{event.interaction.member}-ticket",
            category=tickets_category,
            permission_overwrites=[
                hikari.PermissionOverwrite(
                    id=event.interaction.member,
                    type=1,
                    allow=hikari.Permissions.VIEW_CHANNEL,
                ),
                hikari.PermissionOverwrite(
                    id=default_role, type=0, deny=hikari.Permissions.VIEW_CHANNEL
                ),
            ],
        )
        embed = await ticket_channel_embed(event, bot)
        control_message = await ticket_channel.send(
            f"{event.interaction.member.mention}, please state your problems here.",
            user_mentions=True,
            embed=embed,
            component=(
                event.app.rest.build_action_row()
                .add_button(ButtonStyle.PRIMARY, "close_ticket")
                .set_emoji("🔒")
                .set_label("Close Ticket")
                .add_to_container()
            ),
        )
    else:
        await ticket_channel.send(
            f"{event.interaction.member.mention}, please state your problems here",
            user_mentions=True,
        )


TICKETS = ticket_component.with_slash_command(
    tanjun.slash_command_group("tickets", "Work with tickets [Staff Only]")
)


@TICKETS.with_command
@tanjun.with_owner_check
@tanjun.as_slash_command("startup", "Ensures your guild is configured for tickets!")
async def startup_tickets(
    ctx: tanjun.SlashContext,
    bot: hikari.GatewayBot = tanjun.injected(type=hikari.GatewayBotAware),
):
    """Run the setup for the tickets module. Creates a category Tickets and a channel #tickets with a message/embed."""
    guild = ctx.get_guild()
    if not guild:
        return
    roles: CacheMappingView = guild.get_roles()
    default_role: hikari.Role = guild.get_role(roles.get_item_at(0))
    ticket_channel = None
    tickets_category = None

    await ctx.respond("Let met see if I can find a #tickets channel!")
    for channel_id in guild.get_channels():
        channel = guild.get_channel(channel_id)
        if (
            channel.name.lower() == "tickets"
            and channel.type == hikari.ChannelType.GUILD_CATEGORY
        ):
            tickets_category = channel
        if (
            channel.name.lower() == "tickets"
            and channel.type == hikari.ChannelType.GUILD_TEXT
        ):
            ticket_channel = channel
            await ctx.edit_initial_response("Found it!")

    if not ticket_channel:
        await ctx.edit_initial_response("Not found :(\nWould you like to setup now?")

        message_event: hikari.GuildChannelCreateEvent = await collect_response(
            ctx, yes_no_answer_validator, timeout=DEFAULT_TIMEOUT
        )

        if message_event.content.lower() in FALSE_RESP:
            await ctx.edit_initial_response("Okay exiting!")
            return

        await ctx.edit_initial_response("Okay let's get started!")
        ticket_channel = await guild.create_text_channel(
            name="tickets",
            category=guild.get_channel(ctx.channel_id).parent_id,
            permission_overwrites=[
                hikari.PermissionOverwrite(
                    id=default_role, type=0, deny=hikari.Permissions.SEND_MESSAGES
                ),
            ],
        )
    last_message = await ticket_channel.fetch_history().limit(1)
    if not last_message:
        await ctx.edit_initial_response("Setting up embed and button.  🔘")
        embed = await ticket_embed(ctx, bot)
        row = (
            ctx.rest.build_action_row()
            .add_button(hikari.ButtonStyle.PRIMARY, "new_ticket")
            .set_label("Start Ticket")
            .set_emoji("💬")
            .add_to_container()
        )
        await ticket_channel.send(embed=embed, component=row)
    if not tickets_category:
        await ctx.edit_initial_response("Setting up Tickets Category and locking!  🔒")
        tickets_category = await guild.create_category(
            name="Tickets",
            permission_overwrites=[
                hikari.PermissionOverwrite(
                    id=default_role, type=0, deny=hikari.Permissions.SEND_MESSAGES
                ),
            ],
        )

    await ctx.edit_initial_response("Everything is setup!")


async def ticket_embed(
    ctx: tanjun.SlashContext, bot: hikari.GatewayBot
) -> hikari.Embed:
    """Provides an embed for the tickets channel."""
    description = (
        "If you need help with something you can submit a ticket! A new channel will "
        "be created and I will walk you through what to do. In that channel you will be "
        "able to talk directly to a Mod to ask questions and have access to send images or "
        "documents that might have private or sensitive information."
    )
    embed = hikari.Embed(
        title="Submit a Ticket, Get Help!", description=description, color=8454399
    )
    embed.set_thumbnail(
        "https://cdn.discordapp.com/attachments/733789542884048906/900079323279663175/85d744c5310511ecb705f23c91500735.png"
    )
    embed.set_author(name=bot.get_me().username, icon=bot.get_me().avatar_url)

    return embed


async def ticket_channel_embed(
    event: hikari.InteractionCreateEvent, bot: hikari.GatewayBot
) -> hikari.Embed:
    """Provides an embed for individual ticket channels."""
    description = (
        "Thanks for submitting a ticket! We take all tickets "
        "very seriously. Please provide a full explanation in this "
        "channel. You can include text, images, files, video, or "
        "documents. \n\nPlease do not ping the Mods or Staff unless "
        "there is a life or death situation. Someone will address it "
        "available."
    )
    embed = hikari.Embed(title="", description=description, color=8454399)
    embed.set_thumbnail(
        "https://cdn.discordapp.com/attachments/733789542884048906/900079323279663175/85d744c5310511ecb705f23c91500735.png"
    )
    embed.set_author(name=bot.get_me().username, icon=bot.get_me().avatar_url)

    return embed


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(ticket_component.copy())
