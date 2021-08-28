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

## Features

- *Simple to complex*. The easy stuff for a simple registry is easy, but rich, replaceable systems are in scope also.
- *Better DX*. Improve developer experience through deep embrace of static analysis and usage of symbols instead of magic names.
- *Hierarchical*. A cascade of parent registries helps model request lifecycles.
- *Tested and documented*. High test coverage and quality docs with lots of (tested) examples.- *Extensible*. 

## Requirements

- Python 3.9+.
- venusian (for decorators)

## Installation

You can install *Hopscotch* via [pip](https://pip.pypa.io/) from [PyPI](https://pypi.org/):

```shell
$ pip install hopscotch
```

# Contributing

Contributions are very welcome.
To learn more, see the [contributor's guide](contributing).

# License

Distributed under the terms of the [MIT license](https://opensource.org/licenses/MIT), *Hopscotch* is free and open source software.

# Issues

If you encounter any problems,
please [file an issue](https://github.com/pauleveritt/hopscotch/issues) along with a detailed description.


# Credits

This project was generated from [@cjolowicz's](https://github.com/cjolowicz) [Hypermodern Python Cookiecutter](https://github.com/cjolowicz/cookiecutter-hypermodern-python) template.
