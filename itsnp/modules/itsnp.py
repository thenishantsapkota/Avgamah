from datetime import datetime

import hikari
import tanjun
from hikari import Embed
from hikari.messages import ButtonStyle

from itsnp.core.client import Client
from itsnp.utils.courses import Courses

component = tanjun.Component()
course_obj = Courses()


@component.with_slash_command
@tanjun.with_str_slash_option("course_topic", "Topic the course is about")
@tanjun.as_slash_command("freecourses", "Get a link of free courses.")
async def freecourses_command(ctx: tanjun.abc.Context, *, course_topic: str) -> None:
    course_dict = await course_obj.get_course(course_topic)
    course_title = course_dict["title"].strip()
    course_description = course_dict["description"].replace("\n", "").strip()
    embed = Embed(
        title="Free Udemy Course",
        description=f"**Course Title - **{course_title}\n\n**Description - **{course_description})",
        timestamp=datetime.now().astimezone(),
        color=hikari.Color(0x00FF00),
    )
    button = (
        ctx.rest.build_action_row()
        .add_button(ButtonStyle.LINK, course_dict["direct_link"])
        .set_label("Course Link")
        .add_to_container()
    )

    embed.set_footer(text=f"Requested by {ctx.author}", icon=ctx.author.avatar_url)
    embed.set_image(course_dict["img_link"].strip())

    await ctx.respond(embed=embed, component=button)


@tanjun.as_loader
def load_components(client: Client) -> None:
    client.add_component(component.copy())
