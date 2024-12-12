from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, List, Tuple

from src.rpg_task.entity.skill import Skill, SkillType


@dataclass
class Task(ABC):
	"""Класс, от которого наследуются все задания."""

	task: str
	skills: Union[List[Skill], None]

	@abstractmethod
	def save(self) -> Tuple[str, Union[List[Skill], None]]:
		"""Возвращает данные для сохранения задачи."""

	@abstractmethod
	def __str__(self) -> str:
		"""Возвращает текстовое представление задачи."""

	def str_skills(self) -> str:
		return ', '.join(map(lambda skill: SkillType.descriptin(skill), self.skills))
