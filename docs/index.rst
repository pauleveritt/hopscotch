.. include:: ../README.rst
   :end-before: github-only


TO DOCUMENT
===========

- Handling generics such as Optional
- Plain classes, namedtuples (though service typing might be weird, dataclass)
- What is the PyCharm/typing value of ``Service``?
- Caching of service info
- Context-based registrations
- ``__hopscotch_factory__``
- Parent registries
  * get_best_match and injection recurse up
  * context lookup recurses up
- You can do a ``get`` with a ``context`` that overrides ``registry.context``
- ``registry.get`` gives ``LookupError`` if not registered, but during
  injection, if the target isn't in registry, we treat it like a non-registry
  injection and just construct it. This lets you use an unregistered
  function or dataclass component, from a registered one

.. _Contributor Guide: contributing.html

.. toctree::
   :hidden:
   :maxdepth: 1

   reference
   contributing
   Code of Conduct <codeofconduct>
   License <license>
   Changelog <https://github.com/pauleveritt/hopscotch/releases>
