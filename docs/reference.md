# Reference

`Hopscotch` only has a few public symbols to be used by other packages.
Here's the API.

## Registry

The registry is the central part of Hopscotch.
It mimics the registry in `wired`, `Pyramid`, and `Zope` (all 3 of which use Zope's registry.)

```{eval-rst}
.. autoclass:: hopscotch.Registry
   :members:
```

## injectable

This decorator provides a convenient way for the `venusian`-based scanner in the registry to recursively look for registrations.

```{eval-rst}
.. autoclass:: hopscotch.injectable
   :members:
```

## inject_callable

Sometimes you want injection without a registry.
As an example, `viewdom` works both with and without a registry.
For the latter, it does a simpler form of injection, but with many of the same rules and machinery.

```{eval-rst}
.. autoclass:: hopscotch.inject_callable
   :members:
```

## Registration

When using `inject_callable` directly, you need to make an object with the introspected registration information.
This is the object to use.

```{eval-rst}
.. autoclass:: hopscotch.Registration
   :members:
```

## hopscotch.fixtures

Hopscotch provides some fixtures for use in tests and examples.

### DummyOperator
```{eval-rst}
.. automodule:: hopscotch.fixtures
   :members:
```

### Dataclass Examples

```{eval-rst}
.. automodule:: hopscotch.fixtures.dataklasses
   :members:
```

### Function Examples

```{eval-rst}
.. automodule:: hopscotch.fixtures.functions
   :members:
```

### `NamedTuple` Examples

```{eval-rst}
.. automodule:: hopscotch.fixtures.named_tuples
   :members:
```

### Plain Old Class Examples

```{eval-rst}
.. automodule:: hopscotch.fixtures.plain_classes
   :members:
```