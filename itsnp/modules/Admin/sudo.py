import ast
import asyncio
import contextlib
import inspect
import io
import re
import time
import traceback
import typing
from collections import abc as collections
from datetime import timedelta

import hikari
import tanjun
import yuyo

from itsnp.core.client import Client

sudo_component = tanjun.Component()


def _yields_results(*args: io.StringIO) -> collections.Iterator[str]:
    for name, stream in zip(("stdout", "stderr"), args):
        yield f"- /dev/{name}:"
        while lines := stream.readlines(25):
            yield from (line[:-1] for line in lines)


def build_eval_globals(
    ctx: tanjun.abc.Context, component: tanjun.abc.Component, /
) -> dict[str, typing.Any]:
    return {
        "asyncio": asyncio,
        "app": ctx.shards,
        "bot": ctx.shards,
        "client": ctx.client,
        "component": component,
        "ctx": ctx,
        "hikari": hikari,
        "tanjun": tanjun,
    }


async def eval_python_code(
    ctx: tanjun.abc.Context, component: tanjun.abc.Component, code: str
) -> tuple[io.StringIO, io.StringIO, int, bool]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    # contextlib.redirect_xxxxx doesn't work properly with contextlib.ExitStack
    with contextlib.redirect_stdout(stdout):
        with contextlib.redirect_stderr(stderr):
            start_time = time.perf_counter()
            try:
                await eval_python_code_no_capture(ctx, component, code)
                failed = False
            except Exception:
                traceback.print_exc()
                failed = True
            finally:
                exec_time = round((time.perf_counter() - start_time) * 1000)

    stdout.seek(0)
    stderr.seek(0)
    return stdout, stderr, exec_time, failed


async def eval_python_code_no_capture(
    ctx: tanjun.abc.Context, component: tanjun.abc.Component, code: str
) -> None:
    globals_ = build_eval_globals(ctx, component)
    compiled_code = compile(code, "", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    if compiled_code.co_flags & inspect.CO_COROUTINE:
        await eval(compiled_code, globals_)

    else:
        eval(compiled_code, globals_)


def _read_and_keep_index(stream: io.StringIO) -> str:
    index = stream.tell()
    stream.seek(0)
    data = stream.read()
    stream.seek(index)
    return data


@sudo_component.with_message_command
# @tanjun.with_option("ephemeral_response", "-e", "--ephemeral", converters=bool, default=False, empty_value=True)
@tanjun.with_owner_check
@tanjun.with_option(
    "suppress_response",
    "-s",
    "--suppress",
    converters=bool,
    default=False,
    empty_value=True,
)
@tanjun.with_option(
    "file_output",
    "-f",
    "--file-out",
    "--file",
    converters=bool,
    default=False,
    empty_value=True,
)
@tanjun.with_parser
@tanjun.as_message_command("eval", "exec")
async def eval_command(
    ctx: tanjun.abc.MessageContext,
    file_output: bool = False,
    # ephemeral_response: bool = False,
    suppress_response: bool = False,
    component: tanjun.Component = tanjun.inject(type=tanjun.Component),
    component_client: yuyo.ComponentClient = tanjun.inject(type=yuyo.ComponentClient),
) -> None:
    """Dynamically evaluate a script in the bot's environment.
    This can only be used by the bot's owner.
    Arguments:
        * code: Greedy multi-line string argument of the code to execute. This should be in a code block.
        * suppress_response (-s, --suppress): Whether to suppress this command's confirmation response.
            This defaults to false and will be set to true if no value is provided.
    """
    assert (
        ctx.message.content is not None
    )  # This shouldn't ever be the case in a command client.
    code = re.findall(r"```(?:[\w]*\n?)([\s\S(^\\`{3})]*?)\n*```", ctx.message.content)
    if not code:
        raise tanjun.CommandError("Expected a python code block.")

    if suppress_response:
        await eval_python_code_no_capture(ctx, component, code[0])
        return

    stdout, stderr, exec_time, failed = await eval_python_code(ctx, component, code[0])

    if file_output:
        await ctx.respond(
            attachments=[
                hikari.Bytes(
                    stdout, "stdout.py", mimetype="text/x-python;charset=utf-8"
                ),
                hikari.Bytes(
                    stderr, "stderr.py", mimetype="text/x-python;charset=utf-8"
                ),
            ]
        )
        return

    colour = 0xFF0000 if failed else 0x00FF00
    string_paginator = yuyo.sync_paginate_string(
        _yields_results(stdout, stderr), wrapper="```python\n{}\n```", char_limit=2034
    )
    embed_generator = (
        (
            hikari.UNDEFINED,
            hikari.Embed(
                colour=colour, description=text, title=f"Eval page {page}"
            ).set_footer(text=f"Time taken: {exec_time} ms"),
        )
        for text, page in string_paginator
    )
    response_paginator = yuyo.ComponentPaginator(
        embed_generator,
        authors=[ctx.author.id],
        triggers=(
            yuyo.pagination.LEFT_DOUBLE_TRIANGLE,
            yuyo.pagination.LEFT_TRIANGLE,
            yuyo.pagination.STOP_SQUARE,
            yuyo.pagination.RIGHT_TRIANGLE,
            yuyo.pagination.RIGHT_DOUBLE_TRIANGLE,
        ),
        timeout=timedelta(days=99999),  # TODO: switch to passing None here
    )
    first_response = await response_paginator.get_next_entry()

    async def send_file(ctx_: yuyo.ComponentContext) -> None:
        await ctx_.defer(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        await ctx_.edit_initial_response(
            attachments=[
                hikari.Bytes(
                    _read_and_keep_index(stdout),
                    "stdout.py",
                    mimetype="text/x-python;charset=utf-8",
                ),
                hikari.Bytes(
                    _read_and_keep_index(stderr),
                    "stderr.py",
                    mimetype="text/x-python;charset=utf-8",
                ),
            ]
        )
        await ctx.edit_initial_response(component=response_paginator)

    executor = (
        yuyo.MultiComponentExecutor()  # TODO: add authors here
        .add_executor(response_paginator)
        .add_builder(response_paginator)
        .add_action_row()
        .add_button(hikari.ButtonStyle.SECONDARY, send_file)
        .set_emoji("\N{CARD FILE BOX}\N{VARIATION SELECTOR-16}")
        .add_to_container()
        .add_to_parent()
    )
    assert first_response is not None
    content, embed = first_response
    message = await ctx.respond(
        content=content, embed=embed, components=executor.builders, ensure_result=True
    )
    component_client.set_executor(message, executor)


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(sudo_component.copy())
