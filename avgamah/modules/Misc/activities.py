import json
import logging

import hikari
import httpx
import tanjun

from avgamah.core import Client
from config import bot_config

from . import activities, application_ids

youtube_component = tanjun.Component()


@youtube_component.with_slash_command
@tanjun.with_str_slash_option(
    "activity",
    "Activity you wanna start",
    choices=(x.lower() for x in activities),
)
@tanjun.with_channel_slash_option(
    "channel", "Channel where you want to start the activities(VC Only)"
)
@tanjun.as_slash_command("activity", "Discord Activities")
async def youtube_together(
    ctx: tanjun.abc.Context, channel: hikari.GuildVoiceChannel, activity: str
) -> None:
    url = f"https://discord.com/api/v8/channels/{channel.id}/invites"
    data = json.dumps(
        {
            "target_application_id": application_ids[activity.title()],
            "target_type": 2,
            "max_uses": 0,
        }
    )
    headers = {
        "Authorization": f"Bot {bot_config.token}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, content=data, headers=headers)
        if response.status_code != 200:
            raise tanjun.CommandError(
                "Cannot create the activity right now, try again later."
            )
    response_text = json.loads(response.text)
    try:
        code = response_text["code"]
    except KeyError:
        raise tanjun.CommandError("Cannot find the Invite Code in the response.")

    await ctx.respond(
        f"Click the buttons below to start\nIf the buttons don't work, click on the link below\n> https://discord.com/invite/{code}"
    )


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(youtube_component.copy())
