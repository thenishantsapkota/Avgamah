import typing as t
from pathlib import Path

import tanjun
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

_ClientT = t.TypeVar("_ClientT", bound="Client")


class Client(tanjun.Client):
    __slots__ = tanjun.Client.__slots__ + ("scheduler",)

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)

    def load_modules(self: _ClientT) -> _ClientT:
        return super().load_modules(
            *[f"itsnp.modules.{m.stem}" for m in Path("./itsnp/modules").glob("*.py")]
        )
