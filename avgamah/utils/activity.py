import asyncio
from itertools import cycle
from typing import TYPE_CHECKING

import hikari

if TYPE_CHECKING:
    from avgamah.core.bot import Bot

from avgamah import __version__


class CustomActivity:
    """
    Custom class for defining Bot Presence
    """

    def __init__(self, bot: "Bot") -> None:
        self.bot = bot
        self._statuses = cycle(
            [
                hikari.Activity(
                    type=hikari.ActivityType.STREAMING,
                    name="Sus Things",
                    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                ),
                hikari.Activity(
                    type=hikari.ActivityType.COMPETING,
                    name=f"{len(self.bot.cache.get_available_guilds_view().values())} servers.",
                ),
                hikari.Activity(
                    type=hikari.ActivityType.WATCHING,
                    name=f"{len(self.bot.cache.get_members_view().values())} members",
                ),
                hikari.Activity(
                    type=hikari.ActivityType.WATCHING,
                    name="Slash Commands are here!!",
                ),
                hikari.Activity(
                    type=hikari.ActivityType.WATCHING,
                    name=f"Nothing Sus | Version {__version__}",
                ),
                hikari.Activity(type=hikari.ActivityType.PLAYING, name="Minecraft"),
                hikari.Activity(
                    type=hikari.ActivityType.WATCHING,
                    name="/botinfo to see my source!",
                ),
            ]
        )

    async def change_status(self) -> None:
        """
        Function that changes bot presence every 10 seconds
        """
        while True:
            new_presence = next(self._statuses)
            await self.bot.update_presence(
                activity=new_presence, status=hikari.Status.IDLE
            )
            await asyncio.sleep(20)
