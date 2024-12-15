class EventError(Exception):
	"""Базовый класс для всех ошибок связанных с событиями."""

class SignalTypeError(TypeError, EventError):
	"""Ошибка, возникающая при указании неподходящего сигнала (None)."""

class DispatcherKeyError(KeyError, EventError):
	"""Ошибка, возникающая при указании неизвестного набора (отправитель, сигнал)."""
