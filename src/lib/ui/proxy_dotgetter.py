from __future__ import annotations

from typing import NamedTuple


def main():
    a = DotGetter()
    # print(f"{a.foo.bar=}")  # [out]: ["foo", "bar"]
    # print(f"{a.spam=}")  # [out]: ["foo", "bar", "spam"]
    print(f"{a.foo.bar()=}")
    print(f"{a.spam.eggs()=}")


class DotGetter:
    """
    d = DotGetter()
    d.foo.bar -> ["foo", "bar"]
    d.spam -> ["spam"]
    """

    def __init__(self, path: list[str] | None = None):
        self._path = path if path else []

    def __getattribute__(self, name):
        # special name handling
        if not name.startswith("_") and not name.startswith("__"):
            self_path = object.__getattribute__(self, "_path")
            self_path.append(name)
            return DotGetter(self_path)

        # normal name handling
        object.__setattr__(self, "_path", [])
        return object.__getattribute__(self, name)

    def __call__(self):
        print("foo")
        value = self._path
        object.__setattr__(self, "_path", [])
        return value

    def __repr__(self):
        return str(self._path)


if __name__ == "__main__":
    exit(main())
