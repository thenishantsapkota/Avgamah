import asyncio
import json
import logging
import random
from typing import TYPE_CHECKING

import asyncpraw
import hikari
import tanjun

from config import reddit_config
from itsnp.utils.buttons import DELETE_ROW

if TYPE_CHECKING:
    from itsnp.core import Bot


class CacheRedditPosts:
    def __init__(self, bot: "Bot") -> None:
        self.bot = bot
        self.subreddits = [
            "memes",
            "cursedcomments",
            "boobs",
            "hentai",
            "ass",
            "Nudes",
            "pussy",
        ]
        self.reddit = asyncpraw.Reddit(
            client_id=reddit_config.client_id,
            client_secret=reddit_config.client_secret,
            user_agent="Avgamah",
        )

    async def get_posts(self):
        subreddits = [
            await self.reddit.subreddit(subreddit) for subreddit in self.subreddits
        ]
        data_to_dump = dict()
        for subreddit in subreddits:
            await subreddit.load()

            posts = [
                {
                    "url": post.url,
                    "title": post.title,
                    "permalink": post.permalink,
                }
                async for post in subreddit.hot(limit=100)
            ]

            allowed_extensions = (".gif", ".png", ".jpg", ".jpeg")

            posts = list(
                filter(
                    lambda i: any(
                        (i.get("url").endswith(e) for e in allowed_extensions)
                    ),
                    posts,
                )
            )

            data_to_dump[subreddit.display_name] = posts
            bytes = json.dumps(data_to_dump).encode("utf-8")
            await self.bot.redis.set(subreddit.display_name, bytes)
            logging.info(
                f"Successfully stored posts of {subreddit.display_name} in the cache"
            )

    async def get_random_post(self, subreddit: str) -> dict[str, str]:
        data = await self.bot.redis.get(subreddit)
        data_json = json.loads(data)

        try:
            sub = data_json[subreddit]
        except KeyError:
            raise tanjun.CommandError("Cannot find the data in the cache.")
        else:
            random_post = random.choice(sub)
            return random_post

    async def reddit_sender(self, ctx: tanjun.abc.Context, sub: str) -> None:
        submission = await self.get_random_post(sub)

        embed = hikari.Embed(
            description="**[{}](https://new.reddit.com{})**".format(
                submission.get("title"), submission.get("permalink")
            ),
            color=0x99CCFF,
        )
        embed.set_image(submission.get("url"))
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.respond(embed=embed, component=DELETE_ROW)

    async def fetch_posts(self) -> None:
        while True:
            await self.get_posts()
            await asyncio.sleep(1800)
