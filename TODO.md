# TODO

## Now

## Next

- Bring over the `test_injection` tests
- Write a bunch of examples and hook into docs

## Soon

- A single `__hopscotch__` field to stamp on all generated info
  * But in a parallel registry, rather than mutating the class
- Eliminate top-level `VDOMNode` type
- Bring over `injectable` decorator

## Eventually

- `Context` operator should use a `get_context` method on the registry
  that recurses through parent registries, looking for `context`. Currently
  just uses the current registry. Context might be higher up.
