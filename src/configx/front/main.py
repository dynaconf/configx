"""
Responsible for providing a convenient object to the end-user.
    
"""
from __future__ import annotations

import typing as t
from dataclasses import asdict, dataclass


class BaseSchema:
    def clear(self):
        self.__dynaconf_core__._raw_settings = {}

    def refresh(self):
        try:
            data = self.__dynaconf_core__._raw_settings
            self.__init__(**data)
        except TypeError as e:
            internal_data = self.__dynaconf_core__._raw_settings
            schema_error = str(e)
            raise TypeError(
                f"Current loaded data does not comply with schema:\n{schema_error=}\n{internal_data=}"
            )

    def set(self, key: str, value):
        ...


# https://mypy.readthedocs.io/en/stable/generics.html
T = t.TypeVar("T")


class ConfigManager(t.Generic[T]):
    def __init__(self, schema: type[T], initial_data: t.Optional[dict] = None):
        self.schema = schema
        self._raw_settings = initial_data or {}

    def settings(self) -> T:
        schema_config = self.schema(**self._raw_settings)
        setattr(schema_config, "__dynaconf_core__", self)
        self._schema_config = schema_config
        return schema_config


# Sample Usage
if __name__ == "__main__":

    def main():
        case_initial()

    def get_initial_data():
        return {
            "foo": "old",
            "bar": [1, 2, 3, 4],
            "dicty": {"hello": "world", "is_dicty": True},
            "obj": SomeObj("John", 21),
        }

    @dataclass
    class SomeObj:
        name: str
        age: int

    @dataclass
    class MySchema(BaseSchema):
        foo: str
        bar: list
        dicty: dict
        obj: SomeObj

    def case_initial():
        # core = Core[MySchema](MySchema)
        manager = ConfigManager(schema=MySchema, initial_data=get_initial_data())
        settings = manager.settings()
        print(settings)

        # simulate internal state update
        manager._raw_settings["foo"] = "new"
        # TODO: create another file for those different "fronend" versions
        # manager.refresh(settings) # dumb disposable settings
        # manager.refresh() # global settings kept inside

        settings.refresh()
        print(settings)

        # settings.clear()
        # settings.refresh()
        print(asdict(settings))

    main()
