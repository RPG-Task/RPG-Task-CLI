from typing import Union, List, Tuple, Dict

ListChoices = Union[List[str], Tuple[str], Dict[str, str]]


class Select:
    """
    message (str): Сообщение в поле выбора
    choices (ListChoices): Варианты выбора
    default (int): Стандартный вариант (индекс)
    hide
    """

    def __init__(self, message: str, choices: ListChoices, default: int, blocked: List[int]):
        ...

    def __rich__(self):
        ...


if __name__ == "__main__":
    ...
