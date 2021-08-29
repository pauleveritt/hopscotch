# Future Work

Just to reiterate: I don't expect much adoption of this.
I'm treating it less as "a maybe big package on PyPI" and more like "topics to write articles about."

With that said, here are some places I'm interested in taking this:

## Badass Sphinx "Theme"

Hopscotch is the lowest layer.
Above that are a number of other things, resulting in the real target.
I'd like to make a really neat "theme" that works with Sphinx, Pelican, Pyramid, and whatever.
When I say "theme"...it's a bit of a departure from what's in Sphinx.
Let's just say it that way.

## Kind

I would really like to crack the nut on protocols and really allow implementations that don't subclass, but still fulfill the contract.
I'm skeptical, though: mypy is just pretty overwhelmed with what's on its plate.

One easy first step to improve the developer experience (DX) is to take a page out of Will McGugan's handbook and infer the type.
Let's say we had this:

```python
@injectable()
@dataclass
class AnotherHeading(Heading):
    title: str
```

We could skip needing `@injectable(kind=Heading)` with this logic:

- Get the base classes
- If that class is registered, register this class as a kind

## Precedence

My current scheme for deciding on the best implementation is pretty naive and brittle.
I'd like to restructure the datastructure for the registrations -- for the hundredth time -- to make it more efficient, effective, and simple to get the best match.

## Performance

In a similar sense, lookups are going to be grossly less efficient than the standard Python "go get me this function."
I need it to be a little less gross and possibly rely on caching.

I've tried to think the entire time around ideas of immutability, making decisions up-front, doing work only once, etc.
I can extend it to an idea of: take all the inputs, make a hashable named-tuple, and remember what came out.

## Persistence

"A good Gatsby for Python" has been a target of mine.
I'd like re-render time to be super-fast, but also startup time.
There are ways to remember the introspection results and only update them when software changes.

## Reactive

If you're going to compete with Hugo, and you're in Python...you have to do some tricks.
The biggest being: do the minimal amount work needed on each operation.

I'd like a component system that remembers injection and scribbles down the observer and observable.
Then, when the observable changes, go find everything that injected it, and update it.

Ambitious.
Then again, frontend systems are on their 4th generation of these ideas.

## Configuration Step

At the moment, you can just keep adding registrations to a registry at any time.

Systems like Pyramid have an explicit configuration step which closes at some point.
Hopscotch could benefit from this -- in performance, reliability, and simplicity -- by using this to re-compute more efficient datastructures in the registry.
It could also implement the alternative to "kind=" mentioned above.

## Predicates

Ahh, the really big win.
Pyramid has a concept of registrations with _predicates_: extra kwargs of registration information.
These are then used to find really specific best-fit registrations.
For example, "use this kind of Heading in this section of the site."

I've written this before, for [Decate](https://dectate.readthedocs.io/en/latest/).
It's kind of fun and certainly useful.
