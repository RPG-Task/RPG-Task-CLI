from enum import Enum


class SkillType(Enum):
	STRENGTH = ("Strength", "Сила", "STR")
	DEXTERITY = ("Dexterity", "Ловкость", "DEX")
	INTELLECT = ("Intellect", "Интеллект", "INT")
	CHARISMA = ("Charisma", "Харизма", "CHA")
	CULTURE = ("Culture", "Культура", "CUL")
	CRAFT = ("Craft", "Ремесло", "CRA")

	def __repr__(self):
		return repr(self.name)


class Skill:
	...
