from types import SimpleNamespace
from typing import Any


class A:
    number: int
    string: str
    dict: dict
    list: list

    def __getattribute__(self, name: str) -> Any:
        annotations = object.__getattribute__(self, "__annotations__")
        self_name = object.__getattribute__(self, "__str__")()
        if name in annotations:
            print(f"{name}={annotations[name]}")
        else:
            print(f"{name} do not belong to object")


# a = type("B", (object,), {"number": int})
# class Typespace(SimpleNamespace):
#     def __init__(self, /, **kwargs):
#         super().__init__(**kwargs)
#         type(self).__annotations__.update(**kwargs)


A = type("A", (), {"__annotations__": {"number": int}})
a = A()
# reveal_type(a.foo)
reveal_type(a.number)
# a.foo
# a.number
# a._0
