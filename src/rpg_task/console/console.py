from typing import Any

from rich.console import Console


class RPGTaskConsole:
	def __init__(self):
		self.console = Console()

	def print(self, *args: Any, **kwargs: Any) -> None:
		self.console.print(*args, **kwargs, highlight=False)
