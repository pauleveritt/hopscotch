"""Package wants to manually setup the registry."""
from dataclasses import dataclass

from hopscotch import Registry


@dataclass
class MyConfig:
    """Example configuration class for this fake site."""

    site_title: str


def hopscotch_setup(registry: Registry) -> None:
    """Manually configure the registry for this package."""
    my_config = MyConfig(site_title="My Configuration")
    registry.register(my_config)
