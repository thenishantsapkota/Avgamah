import asyncio
import json
import logging
from typing import TYPE_CHECKING

import aiohttp
import hikari
import tanjun

from avgamah.modules.Misc import zodiac_signs
from avgamah.utils.pagination import paginate
from avgamah.utils.utilities import _chunk

if TYPE_CHECKING:
    from avgamah.core import Bot

logger = logging.getLogger(__name__)


class CacheRashifal:
    def __init__(self, bot: "Bot") -> None:
        self.bot = bot

    async def fetch_rashifal(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://nepalipatro.com.np/rashifal/getv5/type/dwmy"
            ) as resp:
                r = await resp.json()

        bytes_dump = json.dumps(r)
        await self.bot.redis.set("rashifal", bytes_dump)
        logger.info("Stored rashifal in the cache.")

    async def get_rashifal(self) -> dict:
        data = await self.bot.redis.get("rashifal")
        if data is None:
            await self.fetch_rashifal()
            raise tanjun.CommandError("Cannot fetch rashifal, Try again")
        data_json = json.loads(data)

        return data_json

    async def rashifal_sender(
        self, ctx: tanjun.abc.Context, zodiac: str, duration: str
    ) -> None:
        data = await self.get_rashifal()
        rashifal = data["np"][duration]
        iterator = str(rashifal[zodiac]).split("।")
        fields = (
            (
                hikari.UNDEFINED,
                hikari.Embed(
                    title=f"{zodiac_signs[zodiac]}({zodiac.title()})",
                    description="।\n".join(line),
                    color=0x00FF00,
                )
                .set_author(name=rashifal["author"], icon=ctx.cache.get_me().avatar_url)
                .set_footer(text=f"Page {index + 1}"),
            )
            for index, line in enumerate(_chunk(iterator, 5))
        )

        await paginate(ctx, fields, 180)

    async def rashifal_job(self) -> None:
        while True:
            await self.fetch_rashifal()
            await asyncio.sleep(3600)
