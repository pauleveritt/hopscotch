# TODO

## Now

## Next

## Soon

- Write a bunch of examples and hook into docs
  - Sybil for docs

## Eventually

- Better concept of "kind" that is hierarchical in the registration
- Switch away from `__call__` to allow multiple renderings
- Service types have a `select` which helps narrow
- Return this repo to a `src` layout and get coverage working again in GHA
- Bring over predicates
- Hierarchical cache service
  - Including simple persistent based on shelve
  - Get the context and predicate into into a hashable "arguments"
- Write example of a `select` that uses predicates
  - Convert `context` to be part of predicates
- Eliminate top-level `VDOMNode` type
- `Context` operator should use a `get_context` method on the registry
  that recurses through parent registries, looking for `context`. Currently
  just uses the current registry. Context might be higher up.
- Registries have props that can be more easily injected than singletons


## TO DOCUMENT

- Handling generics such as Optional
- Plain classes, namedtuples (though service typing might be weird, dataclass)
- Caching of service info
- Context-based registrations
- `__hopscotch_factory__`
- Parent registries
  - get_best_match and injection recurse up
  - context lookup recurses up
- You can do a `get` with a `context` that overrides `registry.context`
- `registry.get` gives `LookupError` if not registered, but during
  injection, if the target isn't in registry, we treat it like a non-registry
  injection and just construct it. This lets you use an unregistered
  function or dataclass component, from a registered one
- Sniffing base class for "servicetype" on the way to richer system of "kind"
- Inspired by Pyramid
- Venusian makes it cool to decorate
