"""Example objects for tests, examples, and docs."""
from dataclasses import dataclass

from hopscotch.registry import Registry


@dataclass()
class DummyOperator:
    """Simulate an operator that looks something up."""

    arg: str

    def __call__(self, registry: Registry) -> str:
        """Return the stored argument.

        Args:
            registry: A real or fake hopscotch registry for this operator.

        Returns:
            The result of this DummyOperator.
        """
        return self.arg
