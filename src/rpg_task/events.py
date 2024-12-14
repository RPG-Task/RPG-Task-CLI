from dataclasses import dataclass
from typing import Callable


class Event:
	...


# type не поддерживается в версиях <3.12
Callback = Callable[[Event], None]


@dataclass
class Listener:
	event: Event
	callback: Callable[[Event], None]


def listener(event: Event):
	def decorator(callback: Callback) -> Listener:
		return Listener(event, callback)

	return decorator
