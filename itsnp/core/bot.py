import logging
import os
import typing as t
from datetime import datetime
from pathlib import Path

import hikari
from dotenv import load_dotenv

from itsnp import STDOUT_CHANNEL_ID, TEST_GUILD_ID, __version__

from .client import Client

load_dotenv()

_ITSNP = t.TypeVar("_ITSNP", bound="Bot")


class Bot(hikari.GatewayBot):
    __slots__ = hikari.GatewayBot.__slots__ + ("client", "stdout_channel")

    def __init__(self: _ITSNP) -> None:
        super().__init__(token=os.environ.get("BOT_TOKEN"), intents=hikari.Intents.ALL)

    def create_client(self: _ITSNP) -> None:
        self.client = Client.from_gateway_bot(self, set_global_commands=TEST_GUILD_ID)
        self.client.load_modules()

    def run(self: _ITSNP) -> None:
        self.create_client()

        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)

        super().run(
            activity=hikari.Activity(
                name=f"Nothing Sus | Version {__version__}",
                type=hikari.ActivityType.WATCHING,
            )
        )

    async def on_starting(self: _ITSNP, event: hikari.StartingEvent) -> None:
        logging.info("No Cache yet!")

    async def on_started(self: _ITSNP, event: hikari.StartedEvent) -> None:
        self.client.scheduler.start()
        self.stdout_channel = await self.rest.fetch_channel(STDOUT_CHANNEL_ID)
        embed = hikari.Embed(
            title="Bot Starting!",
            description=f"Testing Bot v{__version__} | Now Online",
            timestamp=datetime.now().astimezone(),
        )
        await self.stdout_channel.send(embed=embed)
        logging.info("Bot is ready!")

    async def on_stopping(self: _ITSNP, event: hikari.StoppingEvent) -> None:
        embed = hikari.Embed(
            title="Bot Stopping!",
            description=f"Testing Bot v{__version__} | Now Offline",
            timestamp=datetime.now().astimezone(),
        )
        await self.stdout_channel.send(embed=embed)
        logging.info("Bot has stopped.")
