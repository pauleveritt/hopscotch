# Hopscotch

[![Coverage Status][codecov-badge]][codecov-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]
[![PyPI][pypi-badge]][pypi-link]
[![Python Version][pypi-badge]][pypi-link]
[![PyPI - Downloads][install-badge]][install-link]
[![License][license-badge]][license-link]
[![Test Status][tests-badge]][tests-link]
[![pre-commit][pre-commit-badge]][pre-commit-link]
[![black][black-badge]][black-link]

[codecov-badge]: https://codecov.io/gh/pauleveritt/hopscotch/branch/main/graph/badge.svg
[codecov-link]: https://codecov.io/gh/pauleveritt/hopscotch
[rtd-badge]: https://readthedocs.org/projects/hopscotch/badge/?version=latest
[rtd-link]: https://hopscotch.readthedocs.io/en/latest/?badge=latest
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black
[pypi-badge]: https://img.shields.io/pypi/v/hopscotch.svg
[pypi-link]: https://pypi.org/project/hopscotch
[install-badge]: https://img.shields.io/pypi/dw/hopscotch?label=pypi%20installs
[install-link]: https://pypistats.org/packages/hopscotch
[license-badge]: https://img.shields.io/pypi/l/hopscotch
[license-link]: https://opensource.org/licenses/MIT
[tests-badge]: https://github.com/pauleveritt/hopscotch/workflows/Tests/badge.svg
[tests-link]: https://github.com/pauleveritt/hopscotch/actions?workflow=Tests
[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit-link]: https://github.com/pre-commit/pre-commit

Writing a decoupled application -- a "pluggable app" -- in Python is a common practice.
Looking for a modern registry that scales from simple use, up to rich dependency injection (DI)?
`hopscotch` is a registry and DI package for Python 3.9+, written to support research into component-driven development for Python's web story.

```{admonition} Let's Be Real
I expect a lot of skepticism.
In fact, I don't expect a lot of adoption.
Instead, I'm using this to learn and write articles.
```

## Features

- _Simple to complex_. The easy stuff for a simple registry is easy, but rich, replaceable systems are in scope also.
- _Better DX_. Improve developer experience through deep embrace of static analysis and usage of symbols instead of magic names.
- _Hierarchical_. A cascade of parent registries helps model request lifecycles.
- _Tested and documented_. High test coverage and quality docs with lots of (tested) examples.- _Extensible_.
- _Great with components_. When used with [`viewdom`](https://viewdom.readthedocs.io), everything is wired up and you can just work in templates.

Hopscotch takes its history from `wired`, which came from `Pyramid`, which came from `Zope`.

## Requirements

- Python 3.9+.
- venusian (for decorators)

## Installation

You can install `Hopscotch` via [pip](https://pip.pypa.io/) from [PyPI](https://pypi.org/):

```shell
$ pip install hopscotch
```

## Quick Examples

Let's look at: a hello world, same but with a decorator, replacement, and multiple choice.

Here's a registry with one "kind of thing" in it:

```python
# One kind of thing
@dataclass
class Greeter:
    """A simple greeter."""

    greeting: str = "Hello!"


registry = Registry()
registry.register(Greeter)
# Later
greeter = registry.get(Greeter)
# greeter.greeting == "Hello!"
```

That's manual registration -- let's try with a decorator:

```python
@injectable()
@dataclass
class Greeter:
    """A simple greeter."""

    greeting: str = "Hello!"


registry = Registry()
registry.scan()
# Later
greeter = registry.get(Greeter)
# greeter.greeting == "Hello!"
```

You're building a pluggable app where people can replace builtins:

```python
# Some site might want to change a built-in.
@injectable(kind=Greeter)
@dataclass
class CustomGreeter:
    """Provide a different ``Greeter`` in this site."""

    greeting: str = "Howdy!"
```

Sometimes you want a `Greeter` but sometimes you want a `FrenchGreeter` -- for example, based on the row of data a request is processing:

```python
@injectable(kind=Greeter, context=FrenchCustomer)
@dataclass
class FrenchGreeter:
    """Provide a different ``Greeter`` in this site."""

    greeting: str = "Bonjour!"

# Much later
child_registry = Registry(
    parent=parent_registry,
    context=french_customer
)
greeter2 = child_registry.get(Greeter)
# greeter2.greeting == "Bonjour!"
```

Finally, have your data constructed for you in rich ways, including custom field "operators":

```python
@injectable()
@dataclass
class SiteConfig:
    punctuation: str = "!"


@injectable()
@dataclass
class Greeter:
    """A simple greeter."""

    punctuation: str = get(SiteConfig, attr="punctuation")
    greeting: str = "Hello"

    def greet(self) -> str:
        """Provide a greeting."""
        return f"{self.greeting}{self.punctuation}"
```

The full code for these examples are in the docs, with more explanation (and many more examples.)

And don't worry, dataclasses aren't required.
Some support is available for plain-old classes, `NamedTuple`, and even functions.

# Contributing

Contributions are very welcome.
To learn more, see the [contributor's guide](contributing).

# License

Distributed under the terms of the [MIT license](https://opensource.org/licenses/MIT), _Hopscotch_ is free and open source software.

# Issues

If you encounter any problems,
please [file an issue](https://github.com/pauleveritt/hopscotch/issues) along with a detailed description.

# Credits

This project was generated from [@cjolowicz's](https://github.com/cjolowicz) [Hypermodern Python Cookiecutter](https://github.com/cjolowicz/cookiecutter-hypermodern-python) template.
