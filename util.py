from types import TracebackType
from typing import Optional, Type


class PrettyPrinter:
    def __init__(self, indent_lvl: int = 0, indentation: str = "  "):
        self.indent_lvl = indent_lvl
        self.indentation = indentation

    def print(self, *msg: str, end: str = "\n"):
        indent = self.indentation * self.indent_lvl
        print(indent, end="")
        print(*msg, end=end)

    def __enter__(self) -> "PrettyPrinter":
        self.indent_lvl += 1
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        self.indent_lvl -= 1
        return None
