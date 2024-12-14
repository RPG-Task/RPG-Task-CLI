class EventError(Exception):
	"""Базовый класс для всех ошибок связанных с событиями."""

class SignalTypeError(TypeError, EventError):
	"""Ошибка при указании неподходящего сигнала (None)."""
