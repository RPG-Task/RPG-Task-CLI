from functools import wraps
from typing import Hashable, Callable

from .dispatcher import subscribe, send, Handler, Any, Event


def publisher(signal: Hashable = Any, sender: object = Any):
    def decorator(function: Callable[..., Event]):
        @wraps(function)
        def wrapper(*args, **kwargs) -> Any:
            result = function(*args, **kwargs)
            send(result, signal, sender)
            return result

        return wrapper

    return decorator

########
# from events import subscribe, publisher, Event
# from sub_main import SubMain
#
#
# class Main:
#     def __init__(self, name: str):
#         self.name = name
#
#         subscribe(self.handler_sub_main_signal, "sub_main_signal", "SubMain")
#
#     @staticmethod
#     def handler_sub_main_signal(event: Event) -> None:
#         print("Сигнал от sub_main обработан!")
#         print(f"{event=}")
#
#     @publisher("main_signal", "Main")
#     def push_info_main_signal(self) -> Event:
#         print("-- Отправляю сигнал в sub_main --")
#         return Event(a="one_info", b="two_info", c="three_info")
#
#
#
# if __name__ == "__main__":
#     main = Main("Ivan")
#     sub_main = SubMain()
#
#     main.push_info_main_signal()
########

########
# from events import subscribe, publisher, Event
#
#
# class SubMain:
#     def __init__(self):
#         subscribe(self.handler_main_signal, "main_signal", "Main")
#
#     @publisher("sub_main_signal", "SubMain")
#     def handler_main_signal(self, event: Event) -> Event:
#         print("Обработан запрос из main")
#         print(f"{event=}")
#
#         print("--Отправляем запрос обратно--")
#         return Event(a=1, b=2)
########
