from __future__ import annotations

from sys import hexversion
from typing import TYPE_CHECKING, Tuple
from weakref import ref, WeakValueDictionary

if TYPE_CHECKING:
	from .dispatcher import Handler

if hexversion >= 0x3000000:
	im_func = '__func__'
	im_self = '__self__'
else:
	im_func = 'im_func'
	im_self = 'im_self'


def safe_ref(target: Handler, on_delete=None):
	"""Возвращает безопасную ссылку на target объект."""
	if hasattr(target, im_self):
		if getattr(target, im_self) is not None:
			assert hasattr(target, im_func), \
				f"safeRef target {target} has {im_self}, but no {im_func}, don't know how to create reference"
			reference = BoundMethodWeakRef(
				target=target,
				on_delete=on_delete
			)
			return reference
	if on_delete is not None:
		return ref(target, on_delete)
	else:
		return ref(target)


class BoundMethodWeakRef(object):
	_all_instances = WeakValueDictionary()

	def __new__(cls, target: Handler, on_delete=None):
		key = cls.calculate_key(target)
		current = cls._all_instances.get(key)

		if current is not None:
			current.deletionMethods.append(on_delete)
			return current
		else:
			base = super(BoundMethodWeakRef, cls).__new__(cls)
			cls._all_instances[key] = base
			base.__init__(target, on_delete)
			return base

	def __init__(self, target: Handler, on_delete=None):
		# noinspection PyShadowingNames, PyUnusedLocal
		def remove(weak, self=self):
			methods = self.deletion_methods[:]

			del self.deletion_methods[:]

			try:
				del self.__class__._all_instances[self.key]
			except KeyError:
				...

			for function in methods:
				try:
					if hasattr(function, "__call__"):
						function(self)
				except Exception as e:
					print(f"Исключение во время safe_ref {self} функция очистки {function}: {e}")

		self.deletion_methods = [on_delete]
		self.key = self.calculate_key(target)
		self.weak_self = ref(getattr(target, im_self), remove)
		self.weak_func = ref(getattr(target, im_func), remove)
		self.self_name = getattr(target, im_self).__class__.__name__
		self.func_name = str(getattr(target, im_func).__name__)

	@staticmethod
	def calculate_key(target: Handler) -> Tuple[int, int]:
		return id(getattr(target, im_self)), id(getattr(target, im_func))

	def __str__(self) -> str:
		return f"{self.__class__.__name__} ({self.self_name}, {self.func_name})"

	def __nonzero__(self) -> bool:
		return self is not None

	__repr__ = __str__
	__bool__ = __nonzero__

	def __cmp__(self, other):
		# todo: Попробовать удалить это.
		if not isinstance(other, self.__class__):
			return self.__class__ == type(other)
		return self.key == other.key

	def __call__(self):
		target = self.weak_self()

		if target is not None:
			function = self.weak_func()

			if function is not None:
				return function.__get__(target)
		return None
