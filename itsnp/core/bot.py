import asyncio
import logging
import os
import typing as t
from datetime import datetime
from pathlib import Path

import hikari
from dotenv import load_dotenv
from tortoise import Tortoise

from itsnp import STDOUT_CHANNEL_ID, TEST_GUILD_ID, __version__
from itsnp.core.tortoise_config import tortoise_config

from .client import Client

load_dotenv()

_ITSNP = t.TypeVar("_ITSNP", bound="Bot")

logger = logging.getLogger("itsnp.main")


class Bot(hikari.GatewayBot):
    """Custom class that initiates Hikari's GatewayBot"""

    __slots__ = hikari.GatewayBot.__slots__ + ("client", "stdout_channel")

    def __init__(self: _ITSNP) -> None:
        super().__init__(token=os.environ.get("BOT_TOKEN"), intents=hikari.Intents.ALL)

    def create_client(self: _ITSNP) -> None:
        """Function that creates the tanjun client"""
        self.client = Client.from_gateway_bot(self, set_global_commands=TEST_GUILD_ID)
        self.client.load_modules()

    def run(self: _ITSNP) -> None:
        """Function that runs the Bot"""
        self.create_client()

        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)

        super().run(
            activity=hikari.Activity(
                name=f"Nothing Sus | Version {__version__}",
                type=hikari.ActivityType.WATCHING,
            ),
            status=hikari.Status.IDLE,
        )

    async def connect_db(self) -> None:
        logger.info("Connecting to Database...")
        await Tortoise.init(tortoise_config)
        logger.info("Connected to Database.")

    async def on_starting(self: _ITSNP, event: hikari.StartingEvent) -> None:
        logger.info("No Cache yet!")
        asyncio.create_task(self.connect_db())

    async def on_started(self: _ITSNP, event: hikari.StartedEvent) -> None:
        self.client.scheduler.start()
        self.stdout_channel = await self.rest.fetch_channel(STDOUT_CHANNEL_ID)
        embed = hikari.Embed(
            title="Bot Starting!",
            description=f"Testing Bot v{__version__} | Now Online",
            timestamp=datetime.now().astimezone(),
        )
        # await self.stdout_channel.send(embed=embed)
        logger.info("Bot is ready!")

    async def on_stopping(self: _ITSNP, event: hikari.StoppingEvent) -> None:
        embed = hikari.Embed(
            title="Bot Stopping!",
            description=f"Testing Bot v{__version__} | Now Offline",
            timestamp=datetime.now().astimezone(),
        )
        # await self.stdout_channel.send(embed=embed)
        logger.info("Bot has stopped.")
