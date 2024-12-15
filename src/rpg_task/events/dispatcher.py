from typing import Callable, Hashable, List, Tuple, Generator
from weakref import ref, ReferenceType

from .errors import SignalTypeError, DispatcherKeyError
from .saferef import safe_ref, BoundMethodWeakRef


class _Parameter:
	def __repr__(self) -> str:
		return self.__class__.__name__


class _Any(_Parameter): ...


class _Anonymous(_Parameter): ...


class Event(dict): ...


Any = _Any()
Anonymous = _Anonymous()

Handler = Callable[[Event], None]
WEAKREF_TYPES = (ReferenceType, BoundMethodWeakRef)

connections = {}
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
		handler = safe_ref(handler, on_delete=_remove_handler)

	sender_key = id(sender)

	if sender_key in connections:
		signals = connections[sender_key]
	else:
		connections[sender_key] = signals = {}

	if sender not in (Any, Anonymous, None):
		# noinspection PyUnusedLocal
		def remove(object, senderkey=sender_key):
			_remove_sender(sender_key=senderkey)

		try:
			weak_sender = ref(sender, remove)
			senders[sender_key] = weak_sender
		except:
			...

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


def disconnect(handler: Handler, signal: Hashable = Any, sender: object = Any, weak: bool = True) -> None:
	"""

	:param handler:
	:param signal:
	:param sender:
	:param weak:
	:return:
	"""

	if signal is None:
		raise SignalTypeError(f"Сигнал не может быть None. ({handler=}, {signal=})")
	if weak:
		handler = safe_ref(handler)

	sender_key = id(sender)

	try:
		signals = connections[sender_key]
		handlers = signals[signal]
	except KeyError:
		raise DispatcherKeyError(f"Не найдено получателей для сигнала {signal} от отправителя {sender}.")

	try:
		_remove_old_back_refs(sender_key, signal, handler, handlers)
	except ValueError:
		raise DispatcherKeyError(f"Нет подключения к приемнику {handler} для получения "
								 f"сигнала {signal} от отправителя {sender}.")

	_cleanup_connections(sender_key, signal)


def send(event: Event, signal: Hashable = Any, sender: object = Any) -> List[Tuple[Handler, Any]]:
	responses = []
	for handler in live_handlers(get_all_handlers(sender, signal)):
		response = handler(event)
		responses.append((handler, response))
	return responses


def get_handlers(sender: object = Any, signal: Hashable = Any) -> List:
	try:
		return connections[id(sender)][signal]
	except KeyError:
		return []


def live_handlers(handlers: Generator[Handler]) -> Generator[Handler]:
	for handler in handlers:
		if isinstance(handler, WEAKREF_TYPES):
			handler = handler()
			if handler is not None:
				yield handler
		else:
			yield handler


def get_all_handlers(sender: object = Any, signal: Hashable = Any) -> Generator[Handler]:
	handlers = {}

	for set in (
			get_handlers(sender, signal), get_handlers(sender=sender),
			get_handlers(signal=signal), get_handlers()
	):
		for handler in set:
			if handler:
				try:
					if handler not in handlers:
						handlers[handler] = 1
						yield handler
				except TypeError:
					...


def _remove_handler(handler: Handler) -> bool:
	"""Отключает приёмник от подключений."""
	if not senders_back:
		return False

	back_key = id(handler)

	try:
		back_set = senders_back.pop(back_key)
	except KeyError:
		return False
	else:
		for sender_key in back_set:
			try:
				signals = list(connections[sender_key].keys())
			except KeyError:
				...
			else:
				for signal in signals:
					try:
						handlers = connections[sender_key][signal]
					except KeyError:
						...
					else:
						try:
							handlers.remove(handler)
						except:
							...
					_cleanup_connections(sender_key, signal)


def _cleanup_connections(sender_key: int, signal: Hashable):
	"""Удаляет все пустые сигналы для sender_key. Удаляет sender_key, если он пустой."""
	try:
		handlers = connections[sender_key][signal]
	except:
		...
	else:
		if not handlers:
			# Никаких подключённых приёмников нет, можно удалять сигнал.
			try:
				signals = connections[sender_key]
			except KeyError:
				...
			else:
				del signals[signal]
				if not signals:
					# Больше нет никаких сигнальных соединений, можно удалять отправителя.
					_remove_sender(sender_key)


def _remove_sender(sender_key: int) -> None:
	"""Удаляет sender_key из подключений."""
	_remove_back_refs(sender_key)

	try:
		del connections[sender_key]
	except KeyError:
		...

	try:
		del senders[sender_key]
	except:
		...


def _remove_back_refs(sender_key: int) -> None:
	"""Удаляет обратные ссылки на sender_key."""
	try:
		signals = connections[sender_key]
	except KeyError:
		...
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
		try:
			set.remove(sender_key)
		except:
			break

	if not set:
		try:
			del senders_back[handler_key]
		except KeyError:
			...

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
		signals = connections.get(signal)

		if signals is not None:
			for s, hands in connections.get(signal, {}).items():
				if s != signal:
					for hand in hands:
						if hand is old_handler:
							flag = True
							break

		if not flag:
			_kill_back_ref(old_handler, sender_key)
			return True
		return False
