import typing as t
from pathlib import Path

import hikari
import tanjun

_ClientT = t.TypeVar("_ClientT", bound="Client")


class Client(tanjun.Client):
    __slots__ = tanjun.Client.__slots__ + ("scheduler",)

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

    def load_modules(self: _ClientT) -> _ClientT:
        path = Path("./avgamah/modules")

        for ext in path.glob(("**/") + "[!_]*.py"):
            super().load_modules(".".join([*ext.parts[:-1], ext.stem]))
        return self


@classmethod
def from_gateway_bot(
    cls,
    bot: hikari.GatewayBotAware,
    /,
    *,
    event_managed: bool = True,
    mention_prefix: bool = False,
    set_global_commands: t.Union[hikari.Snowflake, bool] = False,
) -> "Client":
    constructor: Client = (
        cls(
            rest=bot.rest,
            cache=bot.cache,
            events=bot.event_manager,
            shards=bot,
            event_managed=event_managed,
            mention_prefix=mention_prefix,
            set_global_commands=set_global_commands,
        )
        .set_human_only()
        .set_hikari_trait_injectors(bot)
    )

    return constructor
