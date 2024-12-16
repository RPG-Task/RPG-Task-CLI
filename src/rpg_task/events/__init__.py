from dataclasses import dataclass
from functools import wraps
from typing import Hashable, Callable

from dispatcher import subscribe, send, Handler, Any, Event


@dataclass
class Listener:
	function: Handler
	signal: Hashable
	sender: object
	weak: bool

	def subscribe(self) -> None:
		subscribe(self.function, self.signal, self.sender, self.weak)


def listener(signal: Hashable = Any, sender: object = Any, weak: bool = True) -> Callable[..., Listener]:
	def decorator(function: Handler) -> Listener:
		return Listener(function, signal, sender, weak)

	return decorator


def publisher(signal: Hashable = Any, sender: object = Any) -> Callable:
	def decorator(function: Callable[..., Event]) -> Callable:
		@wraps(function)
		def wrapper(*args, **kwargs) -> Any:
			result = function(*args, **kwargs)
			send(result, signal, sender)
			return result

		return wrapper

	return decorator


if __name__ == "__main__":
	class First:
		def __init__(self):
			self.handler_second_signal.subscribe()

		@staticmethod
		@listener("second signal", "Second")
		def handler_second_signal(event: Event) -> None:
			print(f"Сигнал от класса Second обработан! {event=}")

		@publisher("first signal", "First")
		def publisher_info_main(self, name: str, age: int) -> Event:
			print("--- Отправляю сигнал в Second ---")
			return Event(name=name, age=age)


	class Second:
		def __init__(self):
			self.handler_first_signal.subscribe()

		@staticmethod
		@listener("first signal", "First")
		@publisher("second signal", "Second")
		def handler_first_signal(event: Event) -> Event:
			print(f"Сигнал от класса First обработан! {event=}")
			print("--- Отправляю сигнал в First и Third ---")
			return Event(a=1, b=2, c=3)


	class Third:
		def __init__(self):
			self.handler_second_signal.subscribe()

		@staticmethod
		@listener("second signal", "Second")
		def handler_second_signal(event: Event) -> None:
			print(f"Сигнал от класса Second обработан! {event=}")


	first = First()
	second = Second()
	third = Third()

	first.publisher_info_main("Ivan", 23)
