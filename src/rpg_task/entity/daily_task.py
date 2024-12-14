from typing import Tuple, Union, List

from .abstract.task import Task
from .skill import Skill


class DailyTask(Task):
	def save(self) -> Tuple[str, Union[List[Skill], None]]:
		pass

	def __str__(self) -> str:
		pass
