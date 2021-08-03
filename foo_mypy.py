from dataclasses import dataclass


@dataclass()
class Foo:
    name: str = None


f = Foo()
