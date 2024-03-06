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


class BaseDict(dict):
    def __init__(self, *args, **kwargs):
        self._core = kwargs.pop("__dynaconf_core__", None)
        super().__init__(*args, **kwargs)

    def refresh(self):
        new_data = BaseDict(self._core._raw_settings)
        self.update(new_data)

    def set(self, key: str, value):
        keypath = key.split(".")
        patch = {}
        for i in range(len(keypath) - 1):
            cur = keypath[i]
            next = keypath[i + 1]
            patch[cur] = {next: value}
        self._core._raw_settings.update(patch)
        self.refresh()


# https://mypy.readthedocs.io/en/stable/generics.html
T = t.TypeVar("T")


class Core(t.Generic[T]):
    def __init__(self, schema: type[T], initial_data: t.Optional[dict] = None):
        self.schema = schema
        self._raw_settings = initial_data or {}

    def dict_settings(self) -> BaseDict:
        return BaseDict(self._raw_settings, __dynaconf_core__=self)

    def schema_settings(self) -> T:
        schema = self.schema(**self._raw_settings)
        setattr(schema, "__dynaconf_core__", self)
        return schema


# Sample Usage
if __name__ == "__main__":

    def main():
        schema_settings_test()
        # dict_settings_test()

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

    def schema_settings_test():
        # core = Core[MySchema](MySchema)
        core = Core(schema=MySchema, initial_data=get_initial_data())
        settings = core.schema_settings()
        print(settings)

        # simulate internal state update
        core._raw_settings["foo"] = "new"

        settings.refresh()
        print(settings)

        # settings.clear()
        # settings.refresh()
        print(asdict(settings))

    def dict_settings_test():
        # core = Core[MySchema](MySchema)
        core = Core(schema=MySchema)

        settings = core.dict_settings()
        print(settings)

        # simulate internal state update
        core._raw_settings["foo"] = "new"
        settings.refresh()
        print(settings)

        # set via update
        settings.set("newkey", 1234)
        print(settings)

        # set via update with dotted path
        # settings.core_set("dicty.key.spam", "new_value") # TODO: doest work
        settings.set("dicty.key", "new_value")
        print(settings)

    main()
