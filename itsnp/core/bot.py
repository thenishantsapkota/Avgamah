import asyncio
import logging
import typing as t

import aioredis
import hikari
import lavasnek_rs
import yuyo
from tortoise import Tortoise

from config import bot_config, lavalink_config
from itsnp import TEST_GUILD_ID, __version__
from itsnp.utils.activity import CustomActivity
from itsnp.utils.buttons import DELETE_CUSTOM_ID, delete_message_button
from itsnp.utils.cache import CacheRedditPosts
from tortoise_config import tortoise_config

from .client import Client
from .event_handler import EventHandler

_ITSNP = t.TypeVar("_ITSNP", bound="Bot")

logger = logging.getLogger("itsnp.main")


class Data:
    def __init__(self) -> None:
        self.lavalink: lavasnek_rs.Lavalink = None


class Bot(hikari.GatewayBot):
    """Custom class that initiates Hikari's GatewayBot"""

    def __init__(self) -> None:
        super().__init__(token=bot_config.token, intents=hikari.Intents.ALL)
        self.data = Data()
        self.redis = aioredis.from_url(url="redis://redis")
        self.reddit_cache = CacheRedditPosts(self)
        self.component_client = yuyo.ComponentClient.from_gateway_bot(
            self
        ).set_constant_id(DELETE_CUSTOM_ID, delete_message_button)

    def create_client(self: _ITSNP) -> None:
        """Function that creates the tanjun client"""
        self.client = Client.from_gateway_bot(
            self, declare_global_commands=TEST_GUILD_ID, mention_prefix=True
        )
        self.client.load_modules()

    def run(self: _ITSNP) -> None:
        """Function that runs the Bot"""
        self.create_client()

        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)

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
        asyncio.create_task(CacheRedditPosts(self).fetch_posts())
        builder = (
            lavasnek_rs.LavalinkBuilder(self.get_me().id, bot_config.token)
            .set_host("lavalink")  # lavalink for docker else 127.0.0.1
            .set_password(lavalink_config.password)
        )

        event_handler = EventHandler(self)
        lava_client = await builder.build(event_handler)
        self.data.lavalink = lava_client
        logger.info("Bot is ready!")

    async def on_stopping(self: _ITSNP, event: hikari.StoppingEvent) -> None:
        self.component_client.close()
        logger.info("Bot has stopped.")
