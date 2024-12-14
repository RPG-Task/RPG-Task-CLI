from typing import Callable, Hashable, List
from weakref import ref

from .errors import SignalTypeError


class _Parameter:
	def __repr__(self) -> str:
		return self.__class__.__name__


class _Any(_Parameter): ...


class _Anonymous(_Parameter): ...


class Event(dict): ...


Any = _Any()
Anonymous = _Anonymous()

Handler = Callable[[Event], None]

connection = {}
senders = {}
senders_back = {}


def connect(handler: Handler, signal: Hashable = Any, sender: object = Any, weak: bool = True) -> None:
	"""Подключает обработчик к отправителю сигнала.

	:param handler: Функция, которая будет принимать объект Event.
	:param signal: Сигнал, на который будет реагировать handler.
	:param sender: Отправитель, которому должен ответить получатель.
		Нужен для создания обработчиков с одинаковыми сигналами, но разными отправителями.
	:param weak: Использовать ли слабые ссылки на handler.
	:return: None

	:raise: SignalTypeError
	"""

	if signal is None:
		raise SignalTypeError(f"Сигнал не может быть None. ({handler=}, {signal=})")

	if weak:
		...

	sender_key = id(sender)

	if sender_key in connection:
		signals = connection[sender_key]
	else:
		connection[sender_key] = signals = {}

	if sender not in (Any, Anonymous, None):
		def remove(object, senderkey=sender_key):
			_remove_sender(sender_key=senderkey)

		try:
			weak_sender = ref(sender, remove)
			senders[sender_key] = weak_sender
		except: ...

	handler_key = id(handler)

	if signal in signals:
		handlers = signals[signal]
		_remove_old_back_refs(sender_key, signal, handler, handlers)
	else:
		handlers = signals[signal] = []
	try:
		current = senders_back.get(handler_key)
		if current is None:
			senders_back[handler_key] = current = []
		if sender_key not in current:
			current.append(sender_key)
	except:
		pass

	handlers.append(handler)


def _remove_sender(sender_key: int) -> None:
	"""Удаляет sender_key из подключений."""
	_remove_back_refs(sender_key)

	try: del connection[sender_key]
	except KeyError: ...

	try: del senders[sender_key]
	except: ...


def _remove_back_refs(sender_key: int) -> None:
	"""Удаляет обратные ссылки на sender_key."""
	try:
		signals = connection[sender_key]
	except KeyError:
		signals = None
	else:
		items = signals.items()

		def all_handlers():
			for signal, set_ in items:
				for item in set_:
					yield item

		for handler in all_handlers():
			_kill_back_ref(handler, sender_key)


def _kill_back_ref(handler: Handler, sender_key: int) -> bool:
	"""Удаляет обратную ссылку от получателя к ключу отправки."""
	handler_key = id(handler)
	set: dict = senders_back.get(handler_key, {})

	while sender_key in set:
		try: set.remove(sender_key)
		except: break

	if not set:
		try: del senders_back[handler_key]
		except KeyError: ...

	return True


def _remove_old_back_refs(sender_key: int, signal: Hashable, handler: Handler, handlers: List[Handler]) -> bool:
	try:
		index = handlers.index(handler)
	except ValueError:
		return False
	else:
		old_handler = handlers[index]
		del handlers[index]

		flag = False
		signals = connection.get(signal)

		if signals is not None:
			for s, hands in connection.get(signal, {}).items():
				if s != signal:
					for hand in hands:
						if hand is old_handler:
							flag = True
							break

		if not flag:
			_kill_back_ref(old_handler, sender_key)
			return True
		return False
