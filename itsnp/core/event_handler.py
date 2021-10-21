import logging
from datetime import datetime
from typing import TYPE_CHECKING

from hikari import Embed

if TYPE_CHECKING:
    from .bot import Bot

logger = logging.getLogger("itsnp.core.event_handler")


class EventHandler:
    def __init__(self, bot: "Bot") -> None:
        self.bot = bot

    async def track_start(self, lavalink, event) -> None:
        logger.info(f"Track started on Guild: {event.guild_id}")
        node = await lavalink.get_guild_node(event.guild_id)

        if node:
            data = await node.get_data()
            channel_id = data[event.guild_id]

            channel = self.bot.cache.get_guild_channel(channel_id)

            embed = Embed(
                title="Now Playing",
                color=0x00FF00,
                timestamp=datetime.now().astimezone(),
                description=f"[{node.now_playing.track.info.title}]({node.now_playing.track.info.uri}) [<@{node.now_playing.requester}>]",
            )

            await channel.send(embed=embed)

    async def track_finish(self, lavalink, event):
        logger.info(f"Track finished on Guild: {event.guild_id}")

    async def track_exception(self, lavalink, event):
        logger.warning("Track exception event happened on guild: %d", event.guild_id)

        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not skip:
            await event.message.respond("Nothing to skip")
        else:
            if not node.queue and not node.now_playing:
                await lavalink.stop(event.guild_id)
