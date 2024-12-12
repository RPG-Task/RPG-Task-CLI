from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Union, Literal, Self

from .named import Named


@dataclass
class Scale(Enum):
	_max_value: float = field(default=0.0)
	_value: float = 0.0

	def __post_init__(self) -> None:
		self._max_value = round(float(self._max_value), 2)

	def __iadd__(self, increment: float) -> Self:
		if self._max_value == -1:
			self._value += increment
		else:
			self._value = min(self._max_value, max(0, self._value + increment))
		return self

	def __isub__(self, increment: float) -> Self:
		self._value = max(0, self._value - increment)
		return self

	@property
	def is_filled(self) -> bool:
		return (self._value >= self._max_value) * (self._max_value != -1)

	@property
	def value(self) -> float:
		return self._value

	@property
	def max_value(self) -> Union[float, Literal[-1]]:
		return self._max_value

	@value.setter
	def value(self, new_value: float) -> None:
		if self._max_value == -1:
			self._value = round(float(new_value), 2)
		elif new_value > self._max_value:
			self._value = self._max_value
		else:
			self._value = round(float(new_value), 2)

	@max_value.setter
	def max_value(self, new_max_value: float) -> None:
		if self._value > new_max_value:
			self._value = new_max_value
		self._max_value = new_max_value


class NamedScale(Named, Scale):
	...


class SetScale(NamedScale):
	"""Шкала, в которой можно будет задавать список максимальных значений, и при достижении максимального значения он будет автоматически перехадить на него."""
