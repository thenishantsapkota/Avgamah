import asyncio
import logging
import os
import typing as t
from datetime import datetime, timedelta
from pathlib import Path

import hikari
import lavasnek_rs
import yuyo
from dotenv import load_dotenv
from tortoise import Tortoise

from itsnp import STDOUT_CHANNEL_ID, TEST_GUILD_ID, __version__
from itsnp.utils.activity import CustomActivity
from tortoise_config import tortoise_config

from .client import Client
from .event_handler import EventHandler

load_dotenv()

_ITSNP = t.TypeVar("_ITSNP", bound="Bot")

logger = logging.getLogger("itsnp.main")


class Data:
    def __init__(self) -> None:
        self.lavalink: lavasnek_rs.Lavalink = None


class Bot(hikari.GatewayBot):
    """Custom class that initiates Hikari's GatewayBot"""

    def __init__(self) -> None:
        super().__init__(token=os.environ.get("BOT_TOKEN"), intents=hikari.Intents.ALL)
        self.data = Data()
        self.component_client = yuyo.ComponentClient.from_gateway_bot(self)

    def create_client(self: _ITSNP) -> None:
        """Function that creates the tanjun client"""
        self.client = Client.from_gateway_bot(
            self, declare_global_commands=TEST_GUILD_ID
        )
        self.client.load_modules()

    def run(self: _ITSNP) -> None:
        """Function that runs the Bot"""
        self.create_client()

        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.on_shard_ready)

        super().run()

    async def connect_db(self) -> None:
        logger.info("Connecting to Database...")
        await Tortoise.init(tortoise_config)
        logger.info("Connected to Database.")

    async def on_starting(self: _ITSNP, event: hikari.StartingEvent) -> None:
        self.component_client.open()
        logger.info("No Cache yet!")
        asyncio.create_task(self.connect_db())

    async def on_started(self: _ITSNP, event: hikari.StartedEvent) -> None:
        asyncio.create_task(CustomActivity(self).change_status())
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
        self.component_client.close()
        logger.info("Bot has stopped.")

    async def on_shard_ready(self, event: hikari.ShardReadyEvent) -> None:
        builder = (
            lavasnek_rs.LavalinkBuilder(self.get_me().id, os.environ.get("BOT_TOKEN"))
            .set_host("127.0.0.1")
            .set_password(os.environ.get("LAVALINK_PASSWORD"))
        )

        event_handler = EventHandler(self)
        lava_client = await builder.build(event_handler)
        self.data.lavalink = lava_client
