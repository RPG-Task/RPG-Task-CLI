from functools import wraps
from typing import Hashable, Callable

from .dispatcher import connect, send, Handler, Any, Event


def subscribe(signal: Hashable = Any, sender: object = Any, weak: bool = True) -> Callable[[Handler], Callable]:
	def decorator(function: Handler) -> Callable:
		@wraps(function)
		def wrapper(*args, **kwargs) -> Any:
			connect(function, signal, sender, weak)
			return function(*args, **kwargs)

		return wrapper

	return decorator


def publisher(signal: Hashable = Any, sender: object = Any):
	def decorator(function: Callable[..., Event]):
		@wraps(function)
		def wrapper(*args, **kwargs) -> Any:
			result = function(*args, **kwargs)
			send(result, signal, sender)
			return result

		return wrapper

	return decorator
