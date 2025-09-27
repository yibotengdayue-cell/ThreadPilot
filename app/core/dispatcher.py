from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any, Dict, List, Tuple

# 命令的签名：fn(ctx, args) -> (title, blocks[])
CommandFn = Callable[[dict, List[str]], Tuple[str, List[dict]]]

@dataclass
class Command:
    name: str
    desc: str
    fn: CommandFn

class Dispatcher:
    def __init__(self):
        self._cmds: Dict[str, Command] = {}

    def register(self, name: str, desc: str):
        def deco(fn: CommandFn):
            self._cmds[name] = Command(name, desc, fn)
            return fn
        return deco

    def help_text(self) -> str:
        lines = ["可用命令："]
        for k in sorted(self._cmds.keys()):
            lines.append(f"/{k} - {self._cmds[k].desc}")
        return "\n".join(lines)

    def dispatch(self, text: str, ctx: dict) -> Tuple[str, List[dict]] | None:
        if not text or not text.startswith("/"):
            return None
        parts = text.strip().split()
        cmd = parts[0][1:].lower()
        args = parts[1:]
        if cmd in self._cmds:
            return self._cmds[cmd].fn(ctx, args)
        return ("未知指令", [{"text": f"没有 /{cmd} 。\n\n" + self.help_text()}])

dispatcher = Dispatcher()
