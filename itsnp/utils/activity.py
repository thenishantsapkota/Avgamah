import asyncio
from itertools import cycle
from typing import TYPE_CHECKING

import hikari

if TYPE_CHECKING:
    from itsnp.core.bot import Bot

from itsnp import __version__


class CustomActivity:
    """
    Custom class for defining Bot Presence
    """

    def __init__(self, bot: "Bot") -> None:
        self.bot = bot
        self._statuses = cycle(
            [
                hikari.Activity(
                    type=hikari.ActivityType.PLAYING, name=f"https://discord.itsnp.org"
                ),
                hikari.Activity(
                    type=hikari.ActivityType.WATCHING, name=f"Slash Commands are here!!"
                ),
                hikari.Activity(
                    type=hikari.ActivityType.WATCHING,
                    name=f"Nothing Sus | Version {__version__}",
                ),
                hikari.Activity(type=hikari.ActivityType.PLAYING, name=f"Minecraft"),
                hikari.Activity(
                    type=hikari.ActivityType.WATCHING,
                    name=f"/botinfo to see my source!",
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
            await asyncio.sleep(10)
