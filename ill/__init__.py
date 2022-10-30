import json
import random
from pathlib import Path

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    ElementMatch,
    ParamMatch,
    ElementResult,
    RegexResult,
)
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.saya import Channel

from library.decorator.blacklist import Blacklist
from library.decorator.distribute import Distribution
from library.decorator.function_call import FunctionCall
from library.decorator.switch import Switch
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message

channel = Channel.current()

assets_path = Path(Path(__file__).parent, "assets")
with Path(assets_path, "ill_templates.json").open("r", encoding="UTF-8") as f:
    TEMPLATES = json.loads(f.read())["data"]


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        PrefixMatch(),
        FullMatch("发病"),
        ElementMatch(At, optional=True) @ "at",
        ParamMatch(optional=True) @ "text",
    )
)
@decorate(
    Switch.check(channel.module),
    Distribution.distribute(),
    Blacklist.check(),
    FunctionCall.record(channel.module),
)
async def ill(app: Ariadne, event: MessageEvent, at: ElementResult, text: RegexResult):
    if at.matched:
        _target = at.result.target
        if _target_member := await app.get_member(event.sender.group, _target):
            target = _target_member.name
        else:
            target = _target
    elif text.matched:
        target = text.result.display
    else:
        target = event.sender.name
    await send_message(
        event, MessageChain(random.choice(TEMPLATES).format(target=target)), app.account
    )
