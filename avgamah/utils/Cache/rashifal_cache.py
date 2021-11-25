import asyncio
import json
import logging
from typing import TYPE_CHECKING

import aiohttp
import hikari
import tanjun

from avgamah.modules.Misc import zodiac_signs

if TYPE_CHECKING:
    from avgamah.core import Bot

logger = logging.getLogger(__name__)


class CacheRashifal:
    def __init__(self, bot: "Bot") -> None:
        self.bot = bot

    async def get_rashifal(self):
        for zodiac in zodiac_signs:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://rashifal-api.herokuapp.com/api/{zodiac}"
                ) as resp:
                    r = await resp.json()

            bytes_dump = json.dumps(r)
            await self.bot.redis.set(zodiac, bytes_dump)
            logger.info(f"Stored data for {zodiac}")

    async def get_rashifal_data(self, zodiac: str) -> dict[str, str]:
        data = await self.bot.redis.get(zodiac)
        if data is None:
            raise tanjun.CommandError("No data in the Cache.")
        data_json = json.loads(data)

        return data_json

    async def rashifal_sender(self, ctx: tanjun.abc.Context, zodiac: str) -> None:
        rashifal = await self.get_rashifal_data(zodiac)

        await ctx.respond(
            embed=hikari.Embed(
                title=f"{rashifal['sun_sign']} राशिको राशिफल।",
                description=rashifal["prediction"],
                color=0x00FF00,
            ).set_footer(text=rashifal["date"])
        )

    async def fetch_rashifal(self) -> None:
        while True:
            await self.get_rashifal()
            await asyncio.sleep(3600)
