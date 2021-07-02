# TODO

## Now

## Next

- Get context-specific registrations working and tested

## Soon

- Bring over `injectable` decorator
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
- Write example of a `select` that uses predicates
  * Convert `context` to be part of predicates
  
## Eventually

- Sybil for docs
- Eliminate top-level `VDOMNode` type
- `Context` operator should use a `get_context` method on the registry
  that recurses through parent registries, looking for `context`. Currently
  just uses the current registry. Context might be higher up.
