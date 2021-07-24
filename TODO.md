# TODO

## Now


- Clean up fixtures to reflect (a) subclassing and (b) de-service-ification

- Ensure mypy and friends are happy

- Service types have a `select` which helps narrow

- Remove `Service`

- Make `get_service` check for looking up `str` or stuff in the standard library
  
- Clean up
  * Inline any functions that are only called in one place
  * Check the code path execution to get to the various places
  * Do the field_info on registration
  * Ensure the last registration is the one returned
  * inject_callable should already have the field_infos, don't do 
    the work in there to find the implementation
  
- Context
  * Tests that check:
    - the fixture uses the registry
    - the fixture gets the registry context
  * Injection will get the context

- Generalized registration information
  * `.classes` -> `.services`
  * `.register_service` -> `.register_service`
  * `Registration` named tuple -> `Registration` dataclass slots
  * Store `Registration` with the implementation, rather than just 
    implementation
  * Make it possible to inject the registry context
  * Logic (not in select, as it is first class) that gets based on context
  * Docs

## Next

- Get context-specific registrations working and tested

## Soon

- Bring over `injectable` decorator
- Overhaul `register_service`
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
- Use custom dataclass fields instead of `Annotated`
- Bring over predicates
- Hierarchical cache service
  * Including simple persistent based on shelve
  * Get the context and predicate into into a hashable "arguments"

## Eventually

- Sybil for docs
- Eliminate top-level `VDOMNode` type
- `Context` operator should use a `get_context` method on the registry
  that recurses through parent registries, looking for `context`. Currently
  just uses the current registry. Context might be higher up.
- Registries have props that can be more easily injected than singletons