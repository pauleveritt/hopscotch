"""Example objects for tests, examples, and docs."""
from dataclasses import dataclass


@dataclass()
class DummyGet:
    """Simulate an operator that looks something up."""

    arg: str

    def __call__(self) -> str:
        """Return the stored argument."""
        return self.arg


class Service:
    """FIXME Change me."""

    pass
