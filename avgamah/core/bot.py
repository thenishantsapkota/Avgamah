import asyncio
import logging
import typing as t
from datetime import datetime

import aioredis
import hikari
import lavasnek_rs
import tanjun
import yuyo
from tortoise import Tortoise

from avgamah import STDOUT_CHANNEL_ID, TEST_GUILD_ID, __version__
from avgamah.utils.activity import CustomActivity
from avgamah.utils.buttons import DELETE_CUSTOM_ID, delete_message_button
from avgamah.utils.Cache.rashifal_cache import CacheRashifal
from avgamah.utils.Cache.reddit_cache import CacheRedditPosts
from config import bot_config, lavalink_config
from tortoise_config import tortoise_config

from .client import Client
from .event_handler import EventHandler

_AVGAMAH = t.TypeVar("_AVGAMAH", bound="Bot")

logger = logging.getLogger("avgamah.main")


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
        self.rashifal_cache = CacheRashifal(self)
        self.component_client = yuyo.ComponentClient.from_gateway_bot(
            self, event_managed=False
        ).set_constant_id(DELETE_CUSTOM_ID, delete_message_button)

    def create_client(self: _AVGAMAH) -> None:
        """Function that creates the tanjun client"""
        self.client = Client.from_gateway_bot(
            self, declare_global_commands=True, mention_prefix=True
        )
        (
            self.client.add_client_callback(
                tanjun.ClientCallbackNames.STARTING, self.component_client.open
            ).add_client_callback(
                tanjun.ClientCallbackNames.CLOSING, self.component_client.close
            )
        )
        self.client.set_type_dependency(yuyo.ComponentClient, self.component_client)
        self.client.load_modules()

    def run(self: _AVGAMAH) -> None:
        """Function that runs the Bot"""
        self.create_client()

        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_stopped)

        super().run()

    async def connect_db(self: _AVGAMAH) -> None:
        logger.info("Connecting to Database...")
        await Tortoise.init(tortoise_config)
        logger.info("Connected to Database.")

    async def on_starting(self: _AVGAMAH, _: hikari.StartingEvent) -> None:
        logger.info("No Cache yet!")
        asyncio.create_task(self.connect_db())

    async def on_started(self: _AVGAMAH, _: hikari.StartedEvent) -> None:
        await self.starting_embed()
        asyncio.create_task(CustomActivity(self).change_status())
        asyncio.create_task(CacheRashifal(self).rashifal_job())
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

    async def on_stopping(self: _AVGAMAH, _: hikari.StoppingEvent) -> None:
        logger.info("Bot has stopped.")

    async def on_stopped(self: _AVGAMAH, _: hikari.StoppedEvent) -> None:
        await self.stopping_embed()

    async def starting_embed(self: _AVGAMAH) -> None:
        self.stdout_channel = await self.rest.fetch_channel(STDOUT_CHANNEL_ID)
        embed = (
            hikari.Embed(color=0x00FF00, timestamp=datetime.now().astimezone())
            .set_author(
                name=f"{self.cache.get_me()} has started.",
                icon=self.cache.get_me().avatar_url,
            )
            .set_footer(text="Version 1.0")
        )

        await self.stdout_channel.send(embed=embed)

    async def stopping_embed(self: _AVGAMAH) -> None:
        embed = (
            hikari.Embed(color=0xFF0000, timestamp=datetime.now().astimezone())
            .set_author(
                name=f"{self.cache.get_me()} has stopped.",
                icon=self.cache.get_me().avatar_url,
            )
            .set_footer(text="Version 1.0")
        )

        await self.stdout_channel.send(embed=embed)
