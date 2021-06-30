# TODO

## Now

- A single `__hopscotch__` field to stamp on all generated info
  * But in a parallel registry, rather than mutating the class

## Next

- Bring over `injectable` decorator

## Soon

- Overhaul `register_class`
  * Change name to `register_service`
  * Raise an exception if you try to register a non-service 
- Overhaul `Greeting` and friends
  * Emphasis on the service versions in naming
  * Provide some alternate implementations
  * Have 
- Write a bunch of examples and hook into docs
- File a ticket with poetry plugin about `src`
- Return this repo to a `src` layout and get coverage working again in GHA

## Eventually

- Sybil for docs
- Eliminate top-level `VDOMNode` type
- `Context` operator should use a `get_context` method on the registry
  that recurses through parent registries, looking for `context`. Currently
  just uses the current registry. Context might be higher up.
