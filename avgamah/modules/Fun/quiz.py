import html
import random
from datetime import timedelta

import aiohttp
import hikari
import tanjun
import yuyo

from avgamah.core.client import Client

from . import categories, categories_keys

quiz_component = tanjun.Component()


async def on_select_menu_interaction(ctx: yuyo.ComponentContext):
    raise NotImplementedError


@quiz_component.with_slash_command
@tanjun.with_str_slash_option(
    "difficulty",
    "Choose the difficulty of a question",
    choices=(
        "easy",
        "medium",
        "hard",
    ),
)
@tanjun.with_str_slash_option(
    "category",
    "Category of the Question",
    choices=(c.lower() for c in categories_keys),
)
@tanjun.as_slash_command("quiz", "Get a quiz question")
async def quiz(ctx: tanjun.abc.Context, category: str, difficulty: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://opentdb.com/api.php?amount=1&category={categories[category.title()]}&difficulty={difficulty}"
        ) as resp:
            response = await resp.json()
    results = response["results"][0]
    answers = []

    answers.append(results["correct_answer"])
    for answer in results["incorrect_answers"]:
        answers.append(answer)
    random.shuffle(answers)
    embed = hikari.Embed(
        title=html.unescape(results["question"]),
        description="\n".join(
            f"```{index+1}) {html.unescape(value)}```"
            for index, value in enumerate(answers)
        ),
    )
    select_menu = (
        yuyo.ActionRowExecutor()
        .add_select_menu(on_select_menu_interaction, "select_answers")
        .set_placeholder("Choose an answer from the list")
    )

    for answer in answers:
        select_menu.add_option(html.unescape(answer), answer.lower()).add_to_menu()

    message = await ctx.respond(
        embed=embed,
        component=select_menu.add_to_container(),
        ensure_result=True,
    )

    executor = yuyo.components.WaitFor(
        authors=(ctx.author,), timeout=timedelta(minutes=10)
    )
    ctx.shards.component_client.set_executor(message.id, executor)
    component_ctx = await executor.wait_for()
    for value in component_ctx.interaction.values:
        if value.title() == (results["correct_answer"]).title():
            embed.color = 0x00FF00
            embed.add_field(
                name="Correct Answer!",
                value=f"You chose `{component_ctx.interaction.values[0].title()}`\nGood.\nYou seem smart to me:heart_eyes: ",
            )
            await ctx.edit_initial_response(embed=embed, components=[])
        else:
            embed.color = 0xFF0000
            embed.add_field(
                name="Incorrect Answer",
                value=f"You chose `{component_ctx.interaction.values[0].title()}`\nWhat a loser :rofl:",
                inline=True,
            )
            embed.add_field(
                name="Correct Answer",
                value=results["correct_answer"],
                inline=True,
            )
            await ctx.edit_last_response(embed=embed, components=[])


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(quiz_component.copy())
