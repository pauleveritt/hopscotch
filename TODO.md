# TODO

## Now

## Next

- Get rid of the ``servicetype`` name, switch to: implements, or kind,
  or for_, something else.

## Soon

- Write a bunch of examples and hook into docs
  - Sybil for docs
- File a ticket with poetry plugin about `src`

## Eventually

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
